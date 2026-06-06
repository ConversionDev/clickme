"""파이프라인 StepTrace 기록 (도메인 무관)."""

import time
from collections.abc import Awaitable, Callable
from typing import TypeVar
from uuid import UUID

from app.contracts.simulation_pipeline import StepTrace

T = TypeVar("T")


async def trace_step(
    run_id: UUID,
    node: str,
    fn: Callable[[], Awaitable[T]],
    *,
    model: str = "mock",
    input_ref: str = "",
) -> tuple[T, StepTrace]:
    started = time.perf_counter()
    try:
        result = await fn()
        latency_ms = int((time.perf_counter() - started) * 1000)
        trace = StepTrace(
            run_id=run_id,
            node=node,
            status="ok",
            model=model,
            input_ref=input_ref,
            output_ref="ok",
            latency_ms=latency_ms,
        )
        return result, trace
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        trace = StepTrace(
            run_id=run_id,
            node=node,
            status="error",
            model=model,
            input_ref=input_ref,
            latency_ms=latency_ms,
            error=str(exc),
        )
        raise exc from None
