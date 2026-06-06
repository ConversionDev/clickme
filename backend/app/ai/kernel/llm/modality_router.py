"""Multi-LLM 라우터 — 베이스라인은 mock. bake-off 후 실모델 교체."""

import asyncio
import random

from app.db.enums import AdInputType


class MockLLMRouter:
    """결정적 mock 응답 (run_id 해시 기반 seed)."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def _delay(self) -> float:
        return self._rng.uniform(0.01, 0.05)

    async def analyze(self, input_type: AdInputType, text: dict | None) -> dict:
        await asyncio.sleep(self._delay())
        if input_type == AdInputType.text and text:
            headline = text.get("headline", "")
            return {
                "brandSafety": "safe",
                "emotionalTone": "positive" if "무료" in headline else "neutral",
                "keyThemes": ["혁신", "편의성"] if len(headline) > 10 else ["간결함"],
                "targetAgeGroup": "25-40",
                "estimatedCtr": round(self._rng.uniform(2.5, 5.0), 1),
            }
        return {
            "brandSafety": "safe",
            "emotionalTone": "positive",
            "keyThemes": ["비주얼", "브랜드"],
            "targetAgeGroup": "20-35",
            "estimatedCtr": round(self._rng.uniform(3.0, 6.0), 1),
            "visualElements": ["밝은 색상", "제품 클로즈업"],
        }

    async def react(
        self,
        persona: dict,
        ad_summary: str,
        input_type: AdInputType,
    ) -> dict:
        await asyncio.sleep(self._delay())
        base = self._rng.uniform(0.45, 0.95)
        sentiment = self._rng.uniform(-0.2, 0.9)
        click = sentiment > 0.3 and base > 0.55
        conversion = click and sentiment > 0.5
        return {
            "signals": {
                "attention": round(base, 2),
                "sentiment": round(sentiment, 2),
                "click_intent": click,
                "conversion_intent": conversion,
                "comprehension": round(self._rng.uniform(0.5, 0.95), 2),
                "recall": round(self._rng.uniform(0.45, 0.9), 2),
            },
            "reasoning": f"[{persona.get('segment', '세그먼트')}] {ad_summary}에 대한 mock 반응",
            "confidence": round(self._rng.uniform(0.75, 0.95), 2),
            "tokens_used": self._rng.randint(300, 500),
            "response_time_ms": self._rng.randint(800, 2200),
        }
