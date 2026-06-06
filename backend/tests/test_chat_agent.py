"""채팅 mock 에이전트 테스트."""

import pytest
from app.ai.agents.chat.agent import ChatAgent


@pytest.mark.asyncio
async def test_chat_agent_stream():
    agent = ChatAgent()
    chunks = []
    async for c in agent.stream({"content": "시뮬 결과 요약해줘", "meta": {"simulationId": "abc"}}):
        chunks.append(c)
    text = "".join(chunks)
    assert "abc" in text
    assert len(chunks) > 3
