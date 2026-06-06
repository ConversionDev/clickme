"""베이스라인 E2E — login → projects → ads → sim → report → chat (Neon+seed 필요)."""

import asyncio

import pytest
from httpx import AsyncClient

# seed 고정 UUID
SEED_PROJECT_ID = "10000000-0000-0000-0000-000000000001"
SEED_AD_ID = "20000000-0000-0000-0000-000000000001"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_baseline_e2e_flow(client: AsyncClient, user_token: str):
    """llms.txt 전체 DoD: 로그인→프로젝트→광고→시뮬→리포트→채팅."""
    h = _auth(user_token)

    # projects
    res = await client.get("/api/projects", headers=h)
    assert res.status_code == 200
    projects = res.json()["data"]
    assert any(p["id"] == SEED_PROJECT_ID for p in projects)

    # ads list
    res = await client.get(f"/api/projects/{SEED_PROJECT_ID}/ads", headers=h)
    assert res.status_code == 200
    assert any(a["id"] == SEED_AD_ID for a in res.json()["data"])

    # create text ad
    res = await client.post(
        "/api/ads/text",
        headers=h,
        json={
            "project_id": SEED_PROJECT_ID,
            "name": "E2E 테스트 카피",
            "headline": "테스트 헤드라인",
            "body": "테스트 본문",
            "cta": "지금 시작",
        },
    )
    assert res.status_code == 200
    new_ad_id = res.json()["data"]["id"]

    # simulation (persona 3 — 빠른 mock)
    res = await client.post(
        f"/api/projects/{SEED_PROJECT_ID}/simulations",
        headers=h,
        json={"ad_id": new_ad_id, "persona_count": 3},
    )
    assert res.status_code == 200
    sim_id = res.json()["data"]["id"]
    assert res.json()["data"]["status"] == "running"

    # poll until completed
    for _ in range(40):
        res = await client.get(f"/api/simulations/{sim_id}", headers=h)
        assert res.status_code == 200
        status = res.json()["data"]["status"]
        if status == "completed":
            break
        if status == "failed":
            pytest.fail(res.json()["data"].get("error_message", "simulation failed"))
        await asyncio.sleep(0.25)
    else:
        pytest.fail("simulation did not complete in time")

    # report
    res = await client.get(f"/api/simulations/{sim_id}/report", headers=h)
    assert res.status_code == 200
    assert res.json()["data"]["simulation_id"] == sim_id

    # dashboard
    res = await client.get("/api/dashboard", headers=h)
    assert res.status_code == 200

    # chat SSE
    res = await client.post(
        "/api/chat/sessions",
        headers=h,
        json={"title": "E2E 채팅", "project_id": SEED_PROJECT_ID},
    )
    assert res.status_code == 200
    session_id = res.json()["data"]["id"]

    async with client.stream(
        "POST",
        f"/api/chat/sessions/{session_id}/messages",
        headers=h,
        json={"content": "시뮬 결과 요약해줘", "meta": {"simulationId": sim_id}},
    ) as stream:
        assert stream.status_code == 200
        chunks = []
        async for line in stream.aiter_lines():
            if line.startswith("data:"):
                chunks.append(line)
        assert any("done" in c or "token" in c for c in chunks)

    res = await client.get(f"/api/chat/sessions/{session_id}/messages", headers=h)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 2


@pytest.mark.asyncio
async def test_admin_and_billing(client: AsyncClient, admin_token: str, regular_user_token: str):
    ah = _auth(admin_token)
    uh = _auth(regular_user_token)

    res = await client.get("/api/admin/users", headers=ah)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 5

    res = await client.get("/api/admin/chats", headers=ah)
    assert res.status_code == 200

    res = await client.get("/api/admin/usage", headers=ah)
    assert res.status_code == 200
    assert res.json()["data"]["user_count"] >= 5

    # non-admin forbidden
    res = await client.get("/api/admin/users", headers=uh)
    assert res.status_code == 403

    res = await client.get("/api/billing", headers=uh)
    assert res.status_code == 200
    plans = res.json()["data"]
    assert len(plans) == 3
    assert sum(1 for p in plans if p["is_current"]) == 1
