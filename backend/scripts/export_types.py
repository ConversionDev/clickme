"""Pydantic 계약 → frontend/src/api/types.gen.ts 생성.

`uv run python -m scripts.export_types`
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, get_args, get_origin

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
from app.contracts.simulation_pipeline import (
    PersonaConfig,
    Prediction,
    PredictionKpi,
    Recommendation,
)
from app.contracts.sse import SimulationEvent, SimulationEventType
from app.db.enums import (
    AdInputType,
    AdStatus,
    CampaignObjective,
    ChatRole,
    PlanType,
    ProjectMemberRole,
    ProjectStatus,
    SimulationStatus,
    SimulationType,
    UserRole,
)
from app.domains.admin.dto import (
    AdminChatSessionOut,
    AdminUsageOut,
    AdminUserOut,
    CreateAdminUserRequest,
    PatchAdminUserRequest,
)
from app.domains.ads.dto import AdOut, CreateTextAdRequest
from app.domains.auth.dto import LoginRequest, TokenResponse, UserOut
from app.domains.billing.dto import BillingPlanOut
from app.domains.projects.dto import CreateProjectRequest, ProjectOut, UpdateProjectRequest
from app.domains.reports.dto import DashboardOut, ReportOut
from app.domains.users.dto import (
    OrganizationOut,
    UpdateUserSettingsRequest,
    UserProfileOut,
    UserSettingsOut,
)
from app.shared.envelope import ApiResponse, ErrorCode, ErrorDetail
from pydantic import BaseModel

OUT = Path(__file__).resolve().parents[2] / "frontend" / "src" / "api" / "types.gen.ts"

MODELS: list[type[BaseModel] | type[Enum]] = [
    ErrorCode,
    UserRole,
    PlanType,
    ProjectStatus,
    ProjectMemberRole,
    AdInputType,
    AdStatus,
    SimulationType,
    SimulationStatus,
    ChatRole,
    CampaignObjective,
    ErrorDetail,
    ApiResponse,
    LoginRequest,
    UserOut,
    TokenResponse,
    UserProfileOut,
    UserSettingsOut,
    UpdateUserSettingsRequest,
    OrganizationOut,
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectOut,
    CreateTextAdRequest,
    AdOut,
    CreateSimulationRequest,
    SimulationCreatedOut,
    SimulationSummaryOut,
    SimulationDetailOut,
    PersonaConfig,
    PredictionKpi,
    Prediction,
    Recommendation,
    SimulationEventType,
    SimulationEvent,
    CreateChatSessionRequest,
    ChatSessionOut,
    ChatMessageOut,
    SendChatMessageRequest,
    ReportOut,
    DashboardOut,
    AdminUserOut,
    CreateAdminUserRequest,
    PatchAdminUserRequest,
    AdminChatSessionOut,
    AdminUsageOut,
    BillingPlanOut,
]


def _ts_type(field_type: Any, defs: dict[str, Any], ref_path: str) -> str:
    origin = get_origin(field_type)
    if field_type is type(None):
        return "null"
    if isinstance(field_type, type) and issubclass(field_type, Enum):
        return " | ".join(f'"{m.value}"' for m in field_type)
    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
        return field_type.__name__
    if origin is list:
        (inner,) = get_args(field_type)
        return f"{_ts_type(inner, defs, ref_path)}[]"
    if origin is dict:
        key_t, val_t = get_args(field_type)
        return f"Record<{_ts_type(key_t, defs, ref_path)}, {_ts_type(val_t, defs, ref_path)}>"
    if origin is type(None) or str(field_type) == "NoneType":
        return "null"
    if origin is type | type(None).__class__ or str(origin) in ("typing.Union", "types.UnionType"):
        args = get_args(field_type)
        parts = [_ts_type(a, defs, ref_path) for a in args]
        return " | ".join(dict.fromkeys(parts))
    mapping = {str: "string", int: "number", float: "number", bool: "boolean"}
    if field_type in mapping:
        return mapping[field_type]
    return "unknown"


def _interface(model: type[BaseModel]) -> str:
    schema = model.model_json_schema()
    schema.get("$defs", {})
    lines = [f"export interface {model.__name__} {{"]
    required = set(schema.get("required", []))
    for name, prop in schema.get("properties", {}).items():
        if "$ref" in prop:
            ref_name = prop["$ref"].split("/")[-1]
            ts = ref_name
        elif "anyOf" in prop:
            parts = []
            for item in prop["anyOf"]:
                if item.get("type") == "null":
                    parts.append("null")
                elif "$ref" in item:
                    parts.append(item["$ref"].split("/")[-1])
                elif "type" in item:
                    parts.append(_json_type(item["type"]))
            ts = " | ".join(parts)
        elif prop.get("type") == "array":
            items = prop.get("items", {})
            if "$ref" in items:
                ts = items["$ref"].split("/")[-1] + "[]"
            elif "type" in items:
                ts = _json_type(items["type"]) + "[]"
            else:
                ts = "unknown[]"
        elif "type" in prop:
            ts = _json_type(prop["type"])
        else:
            ts = "unknown"
        opt = "" if name in required else "?"
        lines.append(f"  {name}{opt}: {ts};")
    lines.append("}")
    return "\n".join(lines)


def _json_type(t: str) -> str:
    return {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "object": "Record<string, unknown>",
        "array": "unknown[]",
    }.get(t, "unknown")


def _enum(e: type[Enum]) -> str:
    vals = " | ".join(f'"{m.value}"' for m in e)
    return f"export type {e.__name__} = {vals};"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    chunks = [
        "/** AUTO-GENERATED by `uv run python -m scripts.export_types` — do not edit */",
        "",
        "export type ApiResponse<T> = {",
        "  success: boolean;",
        "  data: T | null;",
        "  message?: string | null;",
        "  error?: ErrorDetail | null;",
        "};",
        "",
    ]
    enums = [m for m in MODELS if isinstance(m, type) and issubclass(m, Enum)]
    bases = [
        m
        for m in MODELS
        if isinstance(m, type) and issubclass(m, BaseModel) and m is not ApiResponse
    ]
    # 의존 타입(ReportOut 등)이 먼저 나오도록 정렬
    base_names = {m.__name__ for m in bases}
    order: dict[str, int] = {}

    def deps(model: type[BaseModel]) -> set[str]:
        schema = model.model_json_schema()
        found: set[str] = set()
        for prop in schema.get("properties", {}).values():
            if "$ref" in prop:
                found.add(prop["$ref"].split("/")[-1])
            if prop.get("type") == "array" and "$ref" in prop.get("items", {}):
                found.add(prop["items"]["$ref"].split("/")[-1])
            for item in prop.get("anyOf", []):
                if "$ref" in item:
                    found.add(item["$ref"].split("/")[-1])
        return found & base_names

    for model in bases:
        order[model.__name__] = len(deps(model))
    bases.sort(key=lambda m: order.get(m.__name__, 0))
    for e in enums:
        chunks.append(_enum(e))
        chunks.append("")
    for model in bases:
        chunks.append(_interface(model))
        chunks.append("")
    text = "\n".join(chunks).rstrip() + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(f"exported {OUT.relative_to(OUT.parents[3])}")


if __name__ == "__main__":
    main()
