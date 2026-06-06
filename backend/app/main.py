"""Click Me 백엔드 진입점 — 라우터 등록 · 예외 핸들러 · CORS."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.domains.admin.router import router as admin_router
from app.domains.ads.router import router as ads_router
from app.domains.auth.router import router as auth_router
from app.domains.billing.router import router as billing_router
from app.domains.chat.router import router as chat_router
from app.domains.health.router import router as health_router
from app.domains.projects.router import router as projects_router
from app.domains.reports.router import router as reports_router
from app.domains.simulations.router import router as simulations_router
from app.domains.users.router import router as users_router
from app.shared.config import settings
from app.shared.exceptions import register_exception_handlers
from app.shared.logging import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    if settings.storage_backend == "local":
        Path(settings.local_storage_dir).mkdir(parents=True, exist_ok=True)
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

if settings.storage_backend == "local":
    uploads = Path(settings.local_storage_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads)), name="uploads")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(ads_router)
app.include_router(simulations_router)
app.include_router(reports_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(billing_router)
