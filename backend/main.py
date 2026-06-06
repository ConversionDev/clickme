"""로컬 개발 진입점.

실행: `uv run python main.py`  (또는 venv 활성화 후 `python main.py`)
프로덕션은 이 파일이 아니라 `uvicorn app.main:app ...` CLI로 띄운다.
환경변수: APP_HOST(기본 127.0.0.1) · APP_PORT(8000) · RELOAD(true)
"""

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() != "false",
    )
