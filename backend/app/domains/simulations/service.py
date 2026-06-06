"""시뮬레이션 유스케이스 — 오케스트레이터 호출 + DB 영속 + SSE."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.analyzer.agent import AnalyzerAgent
from app.ai.kernel.orchestrator import SimulationOrchestrator
from app.ai.kernel.registry import registry
from app.contracts.simulation_api import (
    CreateSimulationRequest,
    SimulationCreatedOut,
    SimulationDetailOut,
    SimulationSummaryOut,
)
from app.contracts.simulation_pipeline import AdAnalysis, AdInput, PersonaConfig
from app.contracts.sse import SimulationEvent, SimulationEventType
from app.domains.simulations.repository import SimulationRepository
from app.db.enums import SimulationStatus
from app.db.models.report import Report
from app.db.models.simulation import PersonaResponse, Simulation
from app.db.session import SessionLocal
from app.shared.events import bus
from app.shared.exceptions import AppException
from app.shared.envelope import ErrorCode


def _ensure_registry() -> None:
    if not registry.has("analyzer"):
        registry.register(AnalyzerAgent())


class SimulationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SimulationRepository(db)
        _ensure_registry()

    async def _assert_project_access(self, project_id: uuid.UUID, user_id: str) -> None:
        project = await self.repo.get_project(project_id)
        if not project:
            raise AppException(ErrorCode.NOT_FOUND, "프로젝트를 찾을 수 없습니다", 404)
        if not await self.repo.is_project_member(project_id, uuid.UUID(user_id)):
            raise AppException(ErrorCode.FORBIDDEN, "프로젝트 접근 권한이 없습니다", 403)

    async def create(
        self,
        project_id: uuid.UUID,
        user_id: str,
        body: CreateSimulationRequest,
    ) -> SimulationCreatedOut:
        await self._assert_project_access(project_id, user_id)
        ad = await self.repo.get_ad_for_project(body.ad_id, project_id)
        if not ad:
            raise AppException(ErrorCode.NOT_FOUND, "광고를 찾을 수 없습니다", 404)

        persona_config = body.persona_config or PersonaConfig(count=body.persona_count)
        persona_config = persona_config.model_copy(update={"count": body.persona_count})

        sim = Simulation(
            project_id=project_id,
            ad_id=body.ad_id,
            created_by=uuid.UUID(user_id),
            simulation_type=body.simulation_type,
            objective=body.objective,
            status=SimulationStatus.running,
            persona_count=body.persona_count,
            persona_config=persona_config.model_dump(mode="json"),
            started_at=datetime.now(timezone.utc),
        )
        await self.repo.create_simulation(sim)
        await self.db.commit()

        asyncio.create_task(_run_background(sim.id))
        return SimulationCreatedOut(id=sim.id, status=sim.status)

    async def get_detail(self, simulation_id: uuid.UUID, user_id: str) -> SimulationDetailOut:
        sim = await self._get_authorized(simulation_id, user_id)
        report_id = None
        if sim.status == SimulationStatus.completed and sim.results_summary:
            from sqlalchemy import select

            res = await self.db.execute(select(Report).where(Report.simulation_id == sim.id))
            report = res.scalar_one_or_none()
            if report:
                report_id = report.id

        summary = sim.results_summary or {}
        return SimulationDetailOut(
            id=sim.id,
            project_id=sim.project_id,
            ad_id=sim.ad_id,
            status=sim.status,
            persona_count=sim.persona_count,
            objective=sim.objective,
            results_summary=sim.results_summary,
            created_at=sim.created_at,
            simulation_type=sim.simulation_type,
            persona_config=sim.persona_config,
            requested_count=sim.requested_count,
            received_count=sim.received_count,
            sample_size=sim.sample_size,
            prediction=summary.get("prediction"),
            recommendation=summary.get("recommendation"),
            report_id=report_id,
            started_at=sim.started_at,
            completed_at=sim.completed_at,
            error_message=sim.error_message,
        )

    async def list_for_project(
        self, project_id: uuid.UUID, user_id: str
    ) -> list[SimulationSummaryOut]:
        await self._assert_project_access(project_id, user_id)
        sims = await self.repo.list_by_project(project_id)
        return [
            SimulationSummaryOut(
                id=s.id,
                project_id=s.project_id,
                ad_id=s.ad_id,
                status=s.status,
                persona_count=s.persona_count,
                objective=s.objective,
                results_summary=s.results_summary,
                created_at=s.created_at,
            )
            for s in sims
        ]

    async def _get_authorized(self, simulation_id: uuid.UUID, user_id: str) -> Simulation:
        sim = await self.repo.get_simulation(simulation_id)
        if not sim:
            raise AppException(ErrorCode.NOT_FOUND, "시뮬레이션을 찾을 수 없습니다", 404)
        await self._assert_project_access(sim.project_id, user_id)
        return sim

    async def execute_pipeline(self, simulation_id: uuid.UUID) -> None:
        sim = await self.repo.get_simulation(simulation_id)
        if not sim:
            return
        ad_row = await self.repo.get_ad_for_project(sim.ad_id, sim.project_id)
        if not ad_row:
            await self._fail(sim, "광고 데이터를 찾을 수 없습니다")
            return

        channel = f"sim:{simulation_id}"
        ad_input = AdInput(
            ad_id=ad_row.id,
            input_type=ad_row.input_type,
            text_content=ad_row.text_content,
            image_url=ad_row.storage_url,
            name=ad_row.name,
        )
        existing_analysis = None
        if ad_row.analysis_result:
            raw = ad_row.analysis_result
            existing_analysis = AdAnalysis(
                brand_safety=raw.get("brandSafety", "safe"),
                emotional_tone=raw.get("emotionalTone", "neutral"),
                key_themes=raw.get("keyThemes", []),
                target_age_group=raw.get("targetAgeGroup"),
                estimated_ctr=raw.get("estimatedCtr"),
                visual_elements=raw.get("visualElements", []),
            )

        persona_config = PersonaConfig.model_validate(
            sim.persona_config or {"count": sim.persona_count}
        )

        async def on_progress(node: str, percent: int, message: str) -> None:
            event = SimulationEvent(
                type=SimulationEventType.progress,
                simulation_id=simulation_id,
                node=node,
                percent=percent,
                message=message,
            )
            await bus.publish(channel, event.model_dump(mode="json"))

        try:
            state = await SimulationOrchestrator().run(
                simulation_id,
                ad_input,
                persona_config,
                sim.objective,
                existing_analysis=existing_analysis,
                on_progress=on_progress,
            )
        except Exception as exc:
            await self._fail(sim, str(exc))
            await bus.publish(
                channel,
                SimulationEvent(
                    type=SimulationEventType.error,
                    simulation_id=simulation_id,
                    message=str(exc),
                ).model_dump(mode="json"),
            )
            return

        sim.requested_count = persona_config.count
        sim.received_count = len(state.reactions)
        sim.sample_size = state.stats.sample_size if state.stats else len(state.reactions)
        sim.results_summary = {
            "overallScore": state.prediction.overall_score if state.prediction else 0,
            "verdict": state.prediction.verdict if state.prediction else "",
            "kpi": state.prediction.kpi.model_dump() if state.prediction else {},
            "prediction": state.prediction.model_dump() if state.prediction else None,
            "recommendation": state.recommendation.model_dump() if state.recommendation else None,
        }
        sim.llm_cost_usd = round(len(state.traces) * 0.01, 4)
        sim.status = SimulationStatus.completed
        sim.completed_at = datetime.now(timezone.utc)

        self.repo.add_persona_responses(
            [
                PersonaResponse(
                    simulation_id=sim.id,
                    persona_id=r.persona_id,
                    segment=r.segment,
                    persona_attributes=r.persona_attributes,
                    signals=r.signals.model_dump(),
                    reasoning=r.reasoning,
                    confidence=r.confidence,
                    is_outlier=r.is_outlier,
                    llm_model="mock",
                )
                for r in state.reactions
            ]
        )
        self.repo.add_report(
            Report(
                simulation_id=sim.id,
                report_data={
                    "executiveSummary": {
                        "overallScore": state.prediction.overall_score if state.prediction else 0,
                        "verdict": state.prediction.verdict if state.prediction else "",
                    },
                    "detailedAnalysis": {
                        "kpi": state.prediction.kpi.model_dump() if state.prediction else {},
                        "topDrivers": state.recommendation.top_drivers if state.recommendation else [],
                        "topObjections": state.recommendation.top_objections if state.recommendation else [],
                    },
                    "actionItems": {
                        "copySuggestions": state.recommendation.copy_suggestions if state.recommendation else [],
                        "ctaSuggestions": state.recommendation.cta_suggestions if state.recommendation else [],
                        "nextABTest": state.recommendation.next_ab_test if state.recommendation else None,
                    },
                },
            )
        )
        await self.db.commit()

        await bus.publish(
            channel,
            SimulationEvent(
                type=SimulationEventType.milestone,
                simulation_id=simulation_id,
                node="report",
                percent=100,
                message="리포트 생성 완료",
            ).model_dump(mode="json"),
        )
        await bus.publish(
            channel,
            SimulationEvent(
                type=SimulationEventType.completed,
                simulation_id=simulation_id,
                percent=100,
                message="시뮬레이션 완료",
                data={"simulation_id": str(simulation_id)},
            ).model_dump(mode="json"),
        )

    async def _fail(self, sim: Simulation, message: str) -> None:
        sim.status = SimulationStatus.failed
        sim.error_message = message
        sim.completed_at = datetime.now(timezone.utc)
        await self.db.commit()


async def _run_background(simulation_id: uuid.UUID) -> None:
    async with SessionLocal() as db:
        await SimulationService(db).execute_pipeline(simulation_id)
