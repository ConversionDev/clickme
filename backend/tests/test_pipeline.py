"""mock 파이프라인 단위 테스트."""
import uuid

import pytest

from app.ai.agents.analyzer.agent import AnalyzerAgent
from app.ai.agents.simulator.pipeline import run_pipeline
from app.ai.kernel.registry import registry
from app.contracts.simulation_pipeline import AdInput, PersonaConfig, SimState
from app.db.enums import AdInputType, CampaignObjective


@pytest.fixture(autouse=True)
def _register_analyzer():
    if not registry.has("analyzer"):
        registry.register(AnalyzerAgent())


@pytest.mark.asyncio
async def test_run_pipeline_produces_prediction():
    run_id = uuid.uuid4()
    state = SimState(
        run_id=run_id,
        objective=CampaignObjective.conversion,
        ad=AdInput(
            ad_id=uuid.uuid4(),
            input_type=AdInputType.text,
            name="테스트 광고",
            text_content={"headline": "무료 체험 시작", "body": "본문", "cta": "시작"},
        ),
    )
    result = await run_pipeline(state, PersonaConfig(count=5))
    assert result.prediction is not None
    assert 0 <= result.prediction.overall_score <= 100
    assert len(result.reactions) == 5
    assert result.stats is not None
    assert result.recommendation is not None
    assert len(result.traces) >= 8
