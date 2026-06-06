"""프로젝트 멤버십 검증 — 도메인 공통."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project, ProjectMember
from app.shared.envelope import ErrorCode
from app.shared.exceptions import AppException


async def get_project_or_404(db: AsyncSession, project_id: uuid.UUID) -> Project:
    project = await db.get(Project, project_id)
    if not project:
        raise AppException(ErrorCode.NOT_FOUND, "프로젝트를 찾을 수 없습니다", 404)
    return project


async def assert_project_member(
    db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID
) -> Project:
    project = await get_project_or_404(db, project_id)
    res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if not res.scalar_one_or_none():
        raise AppException(ErrorCode.FORBIDDEN, "프로젝트 접근 권한이 없습니다", 403)
    return project


async def list_member_project_ids(db: AsyncSession, user_id: uuid.UUID) -> list[uuid.UUID]:
    res = await db.execute(select(ProjectMember.project_id).where(ProjectMember.user_id == user_id))
    return list(res.scalars().all())
