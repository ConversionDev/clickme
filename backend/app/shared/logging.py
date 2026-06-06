"""구조화 로그. ⚠️ 기밀(예산·크리에이티브·시크릿) 평문 로그 금지 — 참조(id/hash)만."""
import logging
import sys

from app.shared.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )


logger = logging.getLogger("clickme")
