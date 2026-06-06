"""pytest 공통 fixture."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.session import engine


@pytest.fixture(autouse=True)
async def _dispose_db_pool_after_test():
    """테스트 간 asyncpg 풀·이벤트루프 충돌 방지."""
    yield
    await engine.dispose()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _login(client: AsyncClient, email: str, password: str) -> str:
    res = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["success"] is True
    return body["data"]["access_token"]


@pytest.fixture
async def user_token(client: AsyncClient) -> str:
    """seed: kim@techstartup.io (project admin)"""
    return await _login(client, "kim@techstartup.io", "Password123!")


@pytest.fixture
async def regular_user_token(client: AsyncClient) -> str:
    """seed: lee@techstartup.io (role=user)"""
    return await _login(client, "lee@techstartup.io", "Password123!")


@pytest.fixture
async def admin_token(client: AsyncClient) -> str:
    """seed: admin@clickme.io"""
    return await _login(client, "admin@clickme.io", "ChangeMe123!")
