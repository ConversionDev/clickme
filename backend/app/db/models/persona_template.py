"""페르소나 템플릿 (재사용).

embedding=RAG용(pgvector, P2). ivfflat 인덱스는 마이그레이션에서 별도 추가.
"""

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin, UUIDMixin


class PersonaTemplate(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "persona_templates"

    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cluster_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
