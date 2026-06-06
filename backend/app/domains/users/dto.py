"""users/org API 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import PlanType, UserRole


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    plan_type: PlanType
    created_at: datetime


class UserProfileOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: UserRole
    organization_id: UUID


class UserSettingsOut(BaseModel):
    theme: str
    notifications: dict


class UpdateUserSettingsRequest(BaseModel):
    theme: str | None = Field(default=None, pattern="^(light|dark)$")
    notifications: dict | None = None
