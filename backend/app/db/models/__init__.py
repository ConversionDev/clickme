"""모든 ORM 모델을 한 곳에서 import → Alembic이 전부 인식 (autogenerate/메타데이터)."""

from app.db.models.ad import Ad
from app.db.models.audit_log import AuditLog
from app.db.models.base import Base
from app.db.models.chat import ChatMessage, ChatSession
from app.db.models.generated_ad import GeneratedAd
from app.db.models.organization import Organization
from app.db.models.persona_template import PersonaTemplate
from app.db.models.project import Project, ProjectMember
from app.db.models.refresh_token import RefreshToken
from app.db.models.report import CalibrationData, Report
from app.db.models.simulation import DebateResult, PersonaResponse, Simulation
from app.db.models.user import User
from app.db.models.user_settings import UserSettings

__all__ = [
    "Base",
    "Organization",
    "User",
    "RefreshToken",
    "UserSettings",
    "Project",
    "ProjectMember",
    "Ad",
    "PersonaTemplate",
    "Simulation",
    "PersonaResponse",
    "DebateResult",
    "Report",
    "CalibrationData",
    "ChatSession",
    "ChatMessage",
    "GeneratedAd",
    "AuditLog",
]
