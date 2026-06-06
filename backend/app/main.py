"""Click Me 백엔드 진입점 — 라우터 등록 · 예외 핸들러 · CORS."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.auth.router import router as auth_router
from app.domains.health.router import router as health_router
from app.shared.config import settings
from app.shared.exceptions import register_exception_handlers
from app.shared.logging import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    yield


app = FastAPI(title="Click Me API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health_router)
app.include_router(auth_router)
