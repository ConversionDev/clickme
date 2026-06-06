"""에이전트 레지스트리 — service는 여기로만 AI 호출."""
from app.ai.kernel.agent import Agent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def has(self, name: str) -> bool:
        return name in self._agents

    def get(self, name: str) -> Agent:
        if name not in self._agents:
            raise KeyError(f"agent not registered: {name}")
        return self._agents[name]


registry = AgentRegistry()
