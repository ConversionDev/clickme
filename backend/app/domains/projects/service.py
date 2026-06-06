"""projects 유스케이스."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.projects.repository import ProjectRepository
from app.domains.projects.schemas import CreateProjectRequest, ProjectOut, UpdateProjectRequest
from app.models.project import Project
from app.models.enums import ProjectStatus
from app.shared.exceptions import AppException
from app.shared.project_access import assert_project_member, get_project_or_404
from app.shared.schemas import ErrorCode


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectRepository(db)

    @staticmethod
    def _out(project: Project, role=None) -> ProjectOut:
        return ProjectOut(
            id=project.id,
            organization_id=project.organization_id,
            created_by=project.created_by,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            my_role=role,
        )

    async def list_mine(self, user_id: str) -> list[ProjectOut]:
        rows = await self.repo.list_for_user(uuid.UUID(user_id))
        return [self._out(p, role) for p, role in rows]

    async def get(self, project_id: uuid.UUID, user_id: str) -> ProjectOut:
        row = await self.repo.get_with_role(project_id, uuid.UUID(user_id))
        if not row:
            raise AppException(ErrorCode.FORBIDDEN, "프로젝트 접근 권한이 없습니다", 403)
        project, role = row
        return self._out(project, role)

    async def create(self, user_id: str, org_id: str, body: CreateProjectRequest) -> ProjectOut:
        project = Project(
            organization_id=uuid.UUID(org_id),
            created_by=uuid.UUID(user_id),
            name=body.name,
            description=body.description,
            status=ProjectStatus.active,
        )
        await self.repo.add(project, uuid.UUID(user_id))
        await self.db.commit()
        await self.db.refresh(project)
        from app.models.enums import ProjectMemberRole

        return self._out(project, ProjectMemberRole.owner)

    async def update(
        self, project_id: uuid.UUID, user_id: str, body: UpdateProjectRequest
    ) -> ProjectOut:
        await assert_project_member(self.db, project_id, uuid.UUID(user_id))
        project = await get_project_or_404(self.db, project_id)
        if body.name is not None:
            project.name = body.name
        if body.description is not None:
            project.description = body.description
        if body.status is not None:
            project.status = body.status
        await self.db.commit()
        await self.db.refresh(project)
        row = await self.repo.get_with_role(project_id, uuid.UUID(user_id))
        role = row[1] if row else None
        return self._out(project, role)

    async def delete(self, project_id: uuid.UUID, user_id: str) -> None:
        row = await self.repo.get_with_role(project_id, uuid.UUID(user_id))
        if not row:
            raise AppException(ErrorCode.FORBIDDEN, "프로젝트 접근 권한이 없습니다", 403)
        _, role = row
        if role.value != "owner":
            raise AppException(ErrorCode.FORBIDDEN, "소유자만 삭제할 수 있습니다", 403)
        project = await get_project_or_404(self.db, project_id)
        await self.db.delete(project)
        await self.db.commit()
