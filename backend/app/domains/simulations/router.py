"""simulations 라우터 — 생성·조회·SSE."""
import asyncio
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.simulation_api import (
    CreateSimulationRequest,
    SimulationCreatedOut,
    SimulationDetailOut,
    SimulationSummaryOut,
)
from app.contracts.sse import SimulationEventType
from app.domains.simulations.service import SimulationService
from app.shared.db import get_db
from app.shared.deps import CurrentUser, get_current_user
from app.shared.events import bus
from app.shared.schemas import ApiResponse, ok

router = APIRouter(prefix="/api", tags=["simulations"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
    "/projects/{project_id}/simulations",
    response_model=ApiResponse[SimulationCreatedOut],
)
async def create_simulation(
    project_id: UUID,
    body: CreateSimulationRequest,
    user: UserDep,
    db: DbDep,
) -> ApiResponse[SimulationCreatedOut]:
    return ok(await SimulationService(db).create(project_id, user.id, body))


@router.get(
    "/projects/{project_id}/simulations",
    response_model=ApiResponse[list[SimulationSummaryOut]],
)
async def list_simulations(
    project_id: UUID,
    user: UserDep,
    db: DbDep,
) -> ApiResponse[list[SimulationSummaryOut]]:
    return ok(await SimulationService(db).list_for_project(project_id, user.id))


@router.get(
    "/simulations/{simulation_id}",
    response_model=ApiResponse[SimulationDetailOut],
)
async def get_simulation(
    simulation_id: UUID,
    user: UserDep,
    db: DbDep,
) -> ApiResponse[SimulationDetailOut]:
    return ok(await SimulationService(db).get_detail(simulation_id, user.id))


@router.get("/simulations/{simulation_id}/events")
async def simulation_events(simulation_id: UUID, user: UserDep, db: DbDep) -> StreamingResponse:
    """SSE — progress · milestone · completed · error."""
    from app.models.enums import SimulationStatus

    detail = await SimulationService(db).get_detail(simulation_id, user.id)
    channel = f"sim:{simulation_id}"
    queue = bus.subscribe(channel)

    async def stream():
        if detail.status in (SimulationStatus.completed, SimulationStatus.failed):
            terminal = (
                SimulationEventType.error.value
                if detail.status == SimulationStatus.failed
                else SimulationEventType.completed.value
            )
            payload = {
                "type": terminal,
                "simulation_id": str(simulation_id),
                "percent": 100,
                "message": detail.error_message or "시뮬레이션 완료",
            }
            yield f"event: {terminal}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
            return
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=120.0)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                event_type = payload.get("type", SimulationEventType.progress.value)
                yield f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                if event_type in (
                    SimulationEventType.completed.value,
                    SimulationEventType.error.value,
                ):
                    break
        finally:
            bus.unsubscribe(channel, queue)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
