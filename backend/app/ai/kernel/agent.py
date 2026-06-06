"""에이전트 공통 인터페이스."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AgentResult(BaseModel):
    output: Any
    model: str = "mock"
    token_in: int = 0
    token_out: int = 0
    latency_ms: int = 0


class Agent(ABC):
    name: str

    @abstractmethod
    async def run(self, payload: dict) -> AgentResult:
        """순수 입력→출력. DB·HTTP 접근 금지."""
