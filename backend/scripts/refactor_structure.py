"""일회성 구조 수술 — app/db 통합 · schemas→dto · envelope · modality_router."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app"
BACKEND = Path(__file__).resolve().parents[1]


def _replace_in_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists() or path.suffix not in {".py", ".ini", ".mako"}:
        return
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")


def _walk_py(base: Path, replacements: list[tuple[str, str]]) -> None:
    for path in base.rglob("*"):
        if path.is_file():
            _replace_in_file(path, replacements)


def main() -> None:
    # 1) 물리 이동
    models_src = ROOT / "models"
    db_dir = ROOT / "db"
    db_models = db_dir / "models"
    if models_src.exists() and not db_models.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(models_src), str(db_models))
        enums = db_models / "enums.py"
        if enums.exists():
            shutil.move(str(enums), str(db_dir / "enums.py"))

    shared_db = ROOT / "shared" / "db.py"
    if shared_db.exists():
        shutil.move(str(shared_db), str(db_dir / "session.py"))

    alembic_src = ROOT / "alembic"
    alembic_dst = db_dir / "alembic"
    if alembic_src.exists() and not alembic_dst.exists():
        shutil.move(str(alembic_src), str(alembic_dst))

    # 2) domains schemas.py → dto.py
    for schemas in (ROOT / "domains").rglob("schemas.py"):
        dto = schemas.with_name("dto.py")
        if not dto.exists():
            schemas.rename(dto)

    envelope_src = ROOT / "shared" / "schemas.py"
    envelope_dst = ROOT / "shared" / "envelope.py"
    if envelope_src.exists() and not envelope_dst.exists():
        envelope_src.rename(envelope_dst)

    llm_router = ROOT / "ai" / "kernel" / "llm" / "router.py"
    modality = ROOT / "ai" / "kernel" / "llm" / "modality_router.py"
    if llm_router.exists() and not modality.exists():
        llm_router.rename(modality)

    # 3) import 치환
    reps = [
        ("from app.db.enums", "from app.db.enums"),
        ("from app.db.models.", "from app.db.models."),
        ("from app.db.models import", "from app.db.models import"),
        ("import app.db.models", "import app.db.models"),
        ("from app.db.session import", "from app.db.session import"),
        ("from app.shared.envelope import", "from app.shared.envelope import"),
        ("app.shared.envelope", "app.shared.envelope"),
        (".dto import", ".dto import"),
        ("domains.auth.dto", "domains.auth.dto"),
        ("from app.ai.kernel.llm.modality_router import", "from app.ai.kernel.llm.modality_router import"),
        ("app/db/alembic", "app/db/alembic"),
        ("app.db.models에서", "app.db.models에서"),
    ]
    _walk_py(BACKEND, reps)
    _replace_in_file(BACKEND / "alembic.ini", [("app/db/alembic", "app/db/alembic")])

    # 4) db/__init__.py
    init = db_dir / "__init__.py"
    if not init.exists():
        init.write_text(
            '"""DB 레이어 — ORM · ENUM · 세션 · Alembic."""\n'
            "from app.db.models import Base\n"
            "from app.db.session import SessionLocal, asyncpg_connect_args, engine, get_db\n\n"
            '__all__ = ["Base", "SessionLocal", "asyncpg_connect_args", "engine", "get_db"]\n',
            encoding="utf-8",
        )

    # 5) models __init__ internal paths
    models_init = db_dir / "models" / "__init__.py"
    if models_init.exists():
        text = models_init.read_text(encoding="utf-8")
        text = text.replace("from app.db.models.", "from app.db.models.")
        models_init.write_text(text, encoding="utf-8")

    # 6) llm __init__
    llm_init = ROOT / "ai" / "kernel" / "llm" / "__init__.py"
    if llm_init.exists():
        llm_init.write_text(
            "from app.ai.kernel.llm.modality_router import MockLLMRouter\n\n"
            '__all__ = ["MockLLMRouter"]\n',
            encoding="utf-8",
        )

    # 7) envelope.py docstring
    if envelope_dst.exists():
        text = envelope_dst.read_text(encoding="utf-8")
        if "schemas" in text[:80]:
            text = text.replace(
                "공통 응답 봉투",
                "HTTP 응답 봉투(envelope) — 도메인 dto·app/contracts와 분리",
                1,
            )
            envelope_dst.write_text(text, encoding="utf-8")

    print("refactor_structure: done")


if __name__ == "__main__":
    main()
