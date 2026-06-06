"""SSE 이벤트 계약 — progress · milestone · completed · error."""
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SimulationEventType(str, Enum):
    progress = "progress"
    milestone = "milestone"
    completed = "completed"
    error = "error"


class SimulationEvent(BaseModel):
    type: SimulationEventType
    simulation_id: UUID
    node: str | None = None
    percent: int | None = None
    message: str | None = None
    data: dict[str, Any] | None = None
