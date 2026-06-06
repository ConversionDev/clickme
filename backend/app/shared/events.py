"""인메모리 SSE pub/sub 버스. ⚠️ 베이스라인 단일 워커 전용.
멀티워커 확장 시 Postgres LISTEN/NOTIFY로 교체 (llms.txt 참고)."""

import asyncio
from collections import defaultdict


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, set[asyncio.Queue]] = defaultdict(set)

    async def publish(self, channel: str, event: dict) -> None:
        for queue in list(self._subs.get(channel, ())):
            await queue.put(event)

    def subscribe(self, channel: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subs[channel].add(queue)
        return queue

    def unsubscribe(self, channel: str, queue: asyncio.Queue) -> None:
        self._subs[channel].discard(queue)
        if not self._subs[channel]:
            self._subs.pop(channel, None)


bus = EventBus()
