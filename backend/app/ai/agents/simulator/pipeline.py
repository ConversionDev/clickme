"""시뮬레이터 파이프라인 — plain async fan-out/fan-in (mock LLM)."""
import asyncio
import statistics
from collections.abc import Awaitable, Callable
from uuid import UUID

from app.ai.kernel.llm.router import MockLLMRouter
from app.ai.kernel.registry import registry
from app.ai.kernel.tracing import trace_step
from app.contracts.simulation_pipeline import (
    AdAnalysis,
    AdInput,
    AggregatedStats,
    Persona,
    PersonaConfig,
    PersonaReaction,
    PersonaSignals,
    Prediction,
    PredictionKpi,
    Recommendation,
    SimState,
    StepTrace,
)

SEGMENTS = [
    "20대 여성",
    "30대 남성",
    "40대 여성",
    "20대 남성",
    "50대 남성",
    "30대 여성",
]
CLUSTERS = [
    "cluster_young_female_worker",
    "cluster_mid_male_worker",
    "cluster_40s_female_homemaker",
    "cluster_young_male_student",
    "cluster_50s_male_selfemployed",
    "cluster_30s_female_freelancer",
]

PIPELINE_NODES = [
    "analyze_ad",
    "generate_personas",
    "run_reactions",
    "validate",
    "aggregate",
    "predict",
    "recommend",
    "report",
]


def _iqr_outliers(values: list[float]) -> set[int]:
    if len(values) < 4:
        return set()
    q1 = statistics.quantiles(values, n=4)[0]
    q3 = statistics.quantiles(values, n=4)[2]
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return {i for i, v in enumerate(values) if v < low or v > high}


async def run_pipeline(
    state: SimState,
    persona_config: PersonaConfig,
    *,
    on_progress: Callable[[str, int, str], Awaitable[None]] | None = None,
) -> SimState:
    """오케스트레이터 노드 순차 실행 + 진행률 콜백."""
    llm = MockLLMRouter(seed=hash(str(state.run_id)) % (2**31))
    total = len(PIPELINE_NODES)

    async def progress(node: str, idx: int, message: str) -> None:
        if on_progress:
            percent = min(99, int((idx / total) * 100))
            await on_progress(node, percent, message)

    # analyze_ad
    await progress("analyze_ad", 0, "광고 객관 분석 중")
    if state.ad and not state.analysis:
        analyzer = registry.get("analyzer")

        async def _analyze() -> AdAnalysis:
            result = await analyzer.run({"ad": state.ad.model_dump(mode="json")})
            return AdAnalysis.model_validate(result.output)

        analysis, trace = await trace_step(state.run_id, "analyze_ad", _analyze)
        state.analysis = analysis
        state.traces.append(trace)

    # generate_personas
    await progress("generate_personas", 1, "페르소나 생성 중")
    count = persona_config.count

    async def _personas() -> list[Persona]:
        personas: list[Persona] = []
        for i in range(count):
            seg = SEGMENTS[i % len(SEGMENTS)]
            personas.append(
                Persona(
                    persona_id=f"persona_{i + 1:03d}",
                    segment=seg,
                    cluster_id=CLUSTERS[i % len(CLUSTERS)],
                    attributes={
                        "age": 22 + (i % 5) * 6,
                        "gender": "female" if i % 2 == 0 else "male",
                        "location": (persona_config.regions or ["서울"])[i % max(1, len(persona_config.regions or ["서울"]))],
                    },
                )
            )
        return personas

    personas, trace = await trace_step(state.run_id, "generate_personas", _personas)
    state.personas = personas
    state.traces.append(trace)

    # run_reactions (fan-out)
    await progress("run_reactions", 2, "페르소나 반응 수집 중")
    ad_summary = state.ad.name
    if state.ad.text_content:
        ad_summary = state.ad.text_content.get("headline", state.ad.name)

    async def _one_reaction(persona: Persona) -> PersonaReaction:
        raw = await llm.react(
            {"segment": persona.segment, **persona.attributes},
            ad_summary,
            state.ad.input_type,
        )
        signals = PersonaSignals.model_validate(raw["signals"])
        return PersonaReaction(
            persona_id=persona.persona_id,
            segment=persona.segment,
            persona_attributes=persona.attributes,
            signals=signals,
            reasoning=raw["reasoning"],
            confidence=raw["confidence"],
        )

    async def _reactions() -> list[PersonaReaction]:
        return list(await asyncio.gather(*[_one_reaction(p) for p in state.personas]))

    reactions, trace = await trace_step(state.run_id, "run_reactions", _reactions)
    state.reactions = reactions
    state.traces.append(trace)

    # validate
    await progress("validate", 3, "이상치 검증 중")

    async def _validate() -> list[PersonaReaction]:
        attentions = [r.signals.attention for r in state.reactions]
        outlier_idx = _iqr_outliers(attentions)
        validated: list[PersonaReaction] = []
        for i, r in enumerate(state.reactions):
            if i in outlier_idx:
                validated.append(r.model_copy(update={"is_outlier": True}))
            else:
                validated.append(r)
        return validated

    validated, trace = await trace_step(state.run_id, "validate", _validate)
    state.reactions = validated
    state.traces.append(trace)

    # aggregate
    await progress("aggregate", 4, "집계 중")
    clean = [r for r in state.reactions if not r.is_outlier] or state.reactions

    async def _aggregate() -> AggregatedStats:
        n = len(clean)
        return AggregatedStats(
            sample_size=n,
            outlier_count=sum(1 for r in state.reactions if r.is_outlier),
            mean_attention=statistics.mean(r.signals.attention for r in clean),
            mean_sentiment=statistics.mean(r.signals.sentiment for r in clean),
            click_intent_rate=sum(1 for r in clean if r.signals.click_intent) / n,
            conversion_intent_rate=sum(1 for r in clean if r.signals.conversion_intent) / n,
            mean_comprehension=statistics.mean(r.signals.comprehension for r in clean),
            mean_recall=statistics.mean(r.signals.recall for r in clean),
            ks_similarity=round(min(0.99, 0.75 + n * 0.01), 2),
        )

    stats, trace = await trace_step(state.run_id, "aggregate", _aggregate)
    state.stats = stats
    state.traces.append(trace)

    # predict
    await progress("predict", 5, "5대 지표 예측 중")

    async def _predict() -> Prediction:
        assert state.stats
        s = state.stats
        kpi = PredictionKpi(
            attention_score=round(s.mean_attention, 2),
            sentiment_score=round((s.mean_sentiment + 1) / 2, 2),
            click_intent_rate=round(s.click_intent_rate, 2),
            conversion_intent_rate=round(s.conversion_intent_rate, 2),
            comprehension_score=round(s.mean_comprehension, 2),
            recall_score=round(s.mean_recall, 2),
        )
        overall = int(
            (
                kpi.attention_score
                + kpi.sentiment_score
                + kpi.click_intent_rate
                + kpi.conversion_intent_rate
                + kpi.comprehension_score
            )
            / 5
            * 100
        )
        verdict = "긍정적 반응 우세" if overall >= 60 else "개선 필요"
        return Prediction(
            overall_score=overall,
            verdict=verdict,
            kpi=kpi,
            confidence=round(statistics.mean(r.confidence for r in clean), 2),
        )

    prediction, trace = await trace_step(state.run_id, "predict", _predict)
    state.prediction = prediction
    state.traces.append(trace)

    # recommend
    await progress("recommend", 6, "개선안 생성 중")

    async def _recommend() -> Recommendation:
        assert state.prediction
        return Recommendation(
            top_drivers=["감성적 카피 공감", "CTA 명확성", "타깃 세그먼트 적합"],
            top_objections=["구체적 혜택 부족", "차별점 미흡"],
            copy_suggestions=["핵심 기능을 헤드라인에 명시", "사회적 증거 추가"],
            cta_suggestions=["7일 무료 체험 시작하기"],
            next_ab_test="감성 vs 기능 중심 카피 A/B 테스트",
        )

    recommendation, trace = await trace_step(state.run_id, "recommend", _recommend)
    state.recommendation = recommendation
    state.traces.append(trace)

    # report (노드 완료 마커)
    await progress("report", 7, "리포트 생성 중")

    async def _report() -> None:
        await asyncio.sleep(0)

    _, trace = await trace_step(state.run_id, "report", _report)
    state.traces.append(trace)

    return state


def build_initial_state(
    run_id: UUID,
    ad: AdInput,
    *,
    objective,
    existing_analysis: AdAnalysis | None = None,
) -> SimState:
    return SimState(
        run_id=run_id,
        objective=objective,
        ad=ad,
        analysis=existing_analysis,
    )
