"""projects 영속 계층."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project, ProjectMember
from app.db.enums import ProjectMemberRole


class ProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Project, ProjectMemberRole]]:
        res = await self.db.execute(
            select(Project, ProjectMember.role)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.updated_at.desc())
        )
        return list(res.all())

    async def get_with_role(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[Project, ProjectMemberRole] | None:
        res = await self.db.execute(
            select(Project, ProjectMember.role)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(Project.id == project_id, ProjectMember.user_id == user_id)
        )
        row = res.first()
        return None if row is None else (row[0], row[1])

    async def add(self, project: Project, owner_id: uuid.UUID) -> None:
        self.db.add(project)
        await self.db.flush()
        self.db.add(
            ProjectMember(project_id=project.id, user_id=owner_id, role=ProjectMemberRole.owner)
        )
