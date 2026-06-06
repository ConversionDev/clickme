"""채팅 에이전트 — mock 토큰 스트리밍 + 시뮬 컨텍스트 참조."""
import asyncio
from collections.abc import AsyncIterator

from app.ai.kernel.agent import Agent, AgentResult


class ChatAgent(Agent):
    name = "chat"

    async def run(self, payload: dict) -> AgentResult:
        text = await self._compose(payload)
        return AgentResult(output=text, token_out=len(text.split()))

    async def stream(self, payload: dict) -> AsyncIterator[str]:
        text = await self._compose(payload)
        words = text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else f" {word}"
            await asyncio.sleep(0.03)
            yield chunk

    async def _compose(self, payload: dict) -> str:
        user_msg = payload.get("content", "")
        simulation_id = (payload.get("meta") or {}).get("simulationId")
        if simulation_id:
            return (
                f"시뮬레이션 `{simulation_id}` 결과를 바탕으로 답변드립니다.\n\n"
                f"요청: {user_msg}\n\n"
                "mock 분석: 긍정적 반응이 우세하며, 30대 남성 세그먼트에서 "
                "실용적 정보 보강이 전환율 개선에 가장 효과적일 것으로 보입니다."
            )
        return (
            f"안녕하세요! Click Me 어시스턴트입니다.\n\n"
            f"질문을 이해했습니다: {user_msg}\n\n"
            "광고 시뮬레이션을 실행하거나 프로젝트 리포트를 참조하면 더 구체적인 답변을 드릴 수 있습니다."
        )
