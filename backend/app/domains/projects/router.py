"""projects 라우터."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.projects.dto import CreateProjectRequest, ProjectOut, UpdateProjectRequest
from app.domains.projects.service import ProjectService
from app.db.session import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.envelope import ApiResponse, ok

router = APIRouter(prefix="/api/projects", tags=["projects"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("", response_model=ApiResponse[list[ProjectOut]])
async def list_projects(user: UserDep, db: DbDep) -> ApiResponse[list[ProjectOut]]:
    return ok(await ProjectService(db).list_mine(user.id))


@router.post("", response_model=ApiResponse[ProjectOut])
async def create_project(
    body: CreateProjectRequest, user: UserDep, db: DbDep
) -> ApiResponse[ProjectOut]:
    return ok(await ProjectService(db).create(user.id, user.org_id, body))


@router.get("/{project_id}", response_model=ApiResponse[ProjectOut])
async def get_project(
    project_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[ProjectOut]:
    return ok(await ProjectService(db).get(project_id, user.id))


@router.patch("/{project_id}", response_model=ApiResponse[ProjectOut])
async def update_project(
    project_id: UUID, body: UpdateProjectRequest, user: UserDep, db: DbDep
) -> ApiResponse[ProjectOut]:
    return ok(await ProjectService(db).update(project_id, user.id, body))


@router.delete("/{project_id}", response_model=ApiResponse[None])
async def delete_project(
    project_id: UUID, user: UserDep, db: DbDep
) -> ApiResponse[None]:
    await ProjectService(db).delete(project_id, user.id)
    return ok(message="프로젝트 삭제 완료")
