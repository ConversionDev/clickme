"""projects API 스키마."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ProjectMemberRole, ProjectStatus


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectOut(BaseModel):
    id: UUID
    organization_id: UUID
    created_by: UUID
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    my_role: ProjectMemberRole | None = None
