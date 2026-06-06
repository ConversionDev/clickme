"""Pydantic 계약 → contracts/*.schema.json 덤프. `uv run python -m scripts.export_contracts`"""

import json
from enum import Enum
from pathlib import Path

from app.contracts.chat_api import (
    ChatMessageOut,
    ChatSessionOut,
    CreateChatSessionRequest,
    SendChatMessageRequest,
)
from app.contracts.simulation_api import (
    CreateSimulationRequest,
    SimulationCreatedOut,
    SimulationDetailOut,
    SimulationSummaryOut,
)
from app.contracts.simulation_pipeline import SimState
from app.contracts.sse import SimulationEvent
from app.domains.auth.dto import LoginRequest, TokenResponse, UserOut
from app.shared.envelope import ApiResponse, ErrorCode
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2] / "contracts"


def _schema_for(model: type[BaseModel] | type[Enum]) -> dict:
    if issubclass(model, Enum):
        return {"type": "string", "enum": [e.value for e in model]}
    return model.model_json_schema()


def _dump(name: str, models: list[type[BaseModel] | type[Enum]]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": name,
        "definitions": {m.__name__: _schema_for(m) for m in models},
    }
    out = ROOT / f"{name}.schema.json"
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"exported {out.relative_to(ROOT.parent)}")


def main() -> None:
    _dump("common", [ApiResponse, ErrorCode])
    _dump("auth", [LoginRequest, TokenResponse, UserOut])
    _dump(
        "simulation",
        [
            CreateSimulationRequest,
            SimulationCreatedOut,
            SimulationSummaryOut,
            SimulationDetailOut,
            SimState,
        ],
    )
    _dump("sse", [SimulationEvent])
    _dump(
        "chat",
        [CreateChatSessionRequest, ChatSessionOut, ChatMessageOut, SendChatMessageRequest],
    )


if __name__ == "__main__":
    main()
    print("Tip: run `uv run python -m scripts.export_types` for frontend types.gen.ts")
