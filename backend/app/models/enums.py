"""PG ENUM 타입 (10종). 04_DB설계.sql과 일치.
⚠️ 지표성 enum(segment 등)은 팀 다같이 논의 후 확정 — 단정 금지 (llms.txt 참고)."""
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class PlanType(str, enum.Enum):
    free = "free"
    professional = "professional"
    enterprise = "enterprise"


class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class ProjectMemberRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class AdInputType(str, enum.Enum):
    image = "image"
    text = "text"
    video = "video"
    url = "url"


class AdStatus(str, enum.Enum):
    pending = "pending"
    analyzing = "analyzing"
    completed = "completed"
    failed = "failed"


class SimulationType(str, enum.Enum):
    ad_reaction = "ad_reaction"
    survey = "survey"


class SimulationStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class CampaignObjective(str, enum.Enum):
    awareness = "awareness"
    conversion = "conversion"
