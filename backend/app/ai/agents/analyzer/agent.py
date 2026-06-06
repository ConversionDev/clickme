"""광고분석 에이전트 — 객관 속성 추출 (mock LLM)."""
from app.ai.kernel.agent import Agent, AgentResult
from app.ai.kernel.llm.router import MockLLMRouter
from app.contracts.simulation_pipeline import AdAnalysis, AdInput


class AnalyzerAgent(Agent):
    name = "analyzer"

    def __init__(self, llm: MockLLMRouter | None = None) -> None:
        self._llm = llm or MockLLMRouter()

    async def run(self, payload: dict) -> AgentResult:
        ad = AdInput.model_validate(payload["ad"])
        raw = await self._llm.analyze(ad.input_type, ad.text_content)
        analysis = AdAnalysis(
            brand_safety=raw.get("brandSafety", "safe"),
            emotional_tone=raw.get("emotionalTone", "neutral"),
            key_themes=raw.get("keyThemes", []),
            target_age_group=raw.get("targetAgeGroup"),
            estimated_ctr=raw.get("estimatedCtr"),
            visual_elements=raw.get("visualElements", []),
        )
        return AgentResult(output=analysis.model_dump())
