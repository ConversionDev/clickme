"""시뮬레이션 오케스트레이터 — registry·pipeline 위임."""
from collections.abc import Awaitable, Callable
from uuid import UUID

from app.ai.agents.simulator.pipeline import build_initial_state, run_pipeline
from app.contracts.simulation_pipeline import AdInput, PersonaConfig, SimState
from app.models.enums import CampaignObjective


class SimulationOrchestrator:
    async def run(
        self,
        run_id: UUID,
        ad: AdInput,
        persona_config: PersonaConfig,
        objective: CampaignObjective,
        *,
        existing_analysis=None,
        on_progress: Callable[[str, int, str], Awaitable[None]] | None = None,
    ) -> SimState:
        state = build_initial_state(
            run_id,
            ad,
            objective=objective,
            existing_analysis=existing_analysis,
        )
        return await run_pipeline(state, persona_config, on_progress=on_progress)
