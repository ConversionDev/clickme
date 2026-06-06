"""ads API 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import AdInputType, AdStatus


class CreateTextAdRequest(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=200)
    headline: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1, max_length=2000)
    cta: str = Field(min_length=1, max_length=200)


class AdOut(BaseModel):
    id: UUID
    project_id: UUID
    created_by: UUID
    name: str
    input_type: AdInputType
    text_content: dict | None = None
    storage_url: str | None = None
    analysis_status: AdStatus
    analysis_result: dict | None = None
    analysis_confidence: float | None = None
    created_at: datetime
    updated_at: datetime
