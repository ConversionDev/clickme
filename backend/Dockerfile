# syntax=docker/dockerfile:1
# 빌드 컨텍스트 = 레포 루트 (루트 단일 .dockerignore 적용) → compose가 context: . 로 호출
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /app

# 의존성 레이어 (소스보다 먼저 → 캐시)
COPY backend/pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev

# 앱 소스
COPY backend/ ./

EXPOSE 8000
# ⚠️ 베이스라인: 단일 워커 (SSE 인메모리 버스와 정합)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
