"""시뮬레이션 파이프라인 노드 입출력 계약 (llms.txt SimState)."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import AdInputType, CampaignObjective


class AdInput(BaseModel):
    ad_id: UUID
    input_type: AdInputType
    text_content: dict | None = None
    image_url: str | None = None
    name: str


class AdAnalysis(BaseModel):
    brand_safety: str = "safe"
    emotional_tone: str = "neutral"
    key_themes: list[str] = Field(default_factory=list)
    target_age_group: str | None = None
    estimated_ctr: float | None = None
    visual_elements: list[str] = Field(default_factory=list)


class PersonaConfig(BaseModel):
    count: int = 20
    age_range: list[int] | None = None
    gender_ratio: dict[str, float] | None = None
    regions: list[str] | None = None
    include_clusters: list[str] | None = None


class Persona(BaseModel):
    persona_id: str
    segment: str
    cluster_id: str | None = None
    attributes: dict = Field(default_factory=dict)


class PersonaSignals(BaseModel):
    attention: float = Field(ge=0, le=1)
    sentiment: float = Field(ge=-1, le=1)
    click_intent: bool
    conversion_intent: bool
    comprehension: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)


class PersonaReaction(BaseModel):
    persona_id: str
    segment: str
    persona_attributes: dict
    signals: PersonaSignals
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    is_outlier: bool = False


class AggregatedStats(BaseModel):
    sample_size: int
    outlier_count: int
    mean_attention: float
    mean_sentiment: float
    click_intent_rate: float
    conversion_intent_rate: float
    mean_comprehension: float
    mean_recall: float
    ks_similarity: float = Field(ge=0, le=1, description="집단 분포 유사도(베이스라인 mock)")


class PredictionKpi(BaseModel):
    attention_score: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=0, le=1)
    click_intent_rate: float = Field(ge=0, le=1)
    conversion_intent_rate: float = Field(ge=0, le=1)
    comprehension_score: float = Field(ge=0, le=1)
    recall_score: float = Field(ge=0, le=1)


class Prediction(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    verdict: str
    kpi: PredictionKpi
    confidence: float = Field(ge=0, le=1)


class Recommendation(BaseModel):
    top_drivers: list[str] = Field(default_factory=list)
    top_objections: list[str] = Field(default_factory=list)
    copy_suggestions: list[str] = Field(default_factory=list)
    cta_suggestions: list[str] = Field(default_factory=list)
    next_ab_test: str | None = None


class StepTrace(BaseModel):
    run_id: UUID
    node: str
    status: Literal["ok", "error"]
    model: str | None = None
    prompt_version: str | None = None
    input_ref: str = ""
    output_ref: str = ""
    latency_ms: int = 0
    token_in: int = 0
    token_out: int = 0
    error: str | None = None


class SimState(BaseModel):
    run_id: UUID
    objective: CampaignObjective = CampaignObjective.conversion
    ad: AdInput
    analysis: AdAnalysis | None = None
    personas: list[Persona] = Field(default_factory=list)
    reactions: list[PersonaReaction] = Field(default_factory=list)
    stats: AggregatedStats | None = None
    prediction: Prediction | None = None
    recommendation: Recommendation | None = None
    traces: list[StepTrace] = Field(default_factory=list)
