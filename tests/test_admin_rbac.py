import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from main import app
from backend.auth.security import create_access_token
from backend.database.session import init_db, AsyncSessionLocal
from backend.models.domain import UserModel

client = TestClient(app)

@pytest.mark.asyncio
async def test_admin_rbac_unauthenticated_access():
    """Unauthenticated requests to admin endpoints must return 401 Unauthorized."""
    await init_db()

    endpoints = [
        "/api/admin/users",
        "/api/admin/tenants",
        "/api/admin/revenue",
        "/api/admin/platform-metrics",
        "/api/admin/system-health",
        "/api/system/status",
        "/api/system/alerts"
    ]

    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 401, f"Expected 401 for unauthenticated request to {ep}, got {res.status_code}"


@pytest.mark.asyncio
async def test_admin_rbac_non_super_admin_forbidden():
    """Authenticated non-super-admin requests to admin endpoints must return 403 Forbidden."""
    await init_db()

    # Seed regular trader user into DB
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserModel).where(UserModel.id == 8802))
        trader_user = res.scalars().first()
        if not trader_user:
            trader_user = UserModel(
                id=8802,
                username="trader_rbac_test",
                email="trader_rbac@lumo.trade",
                password_hash="hash123",
                role="trader"
            )
            session.add(trader_user)
            await session.commit()

    token = create_access_token({"sub": "8802", "email": "trader_rbac@lumo.trade"})
    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        "/api/admin/users",
        "/api/admin/tenants",
        "/api/admin/revenue",
        "/api/admin/platform-metrics",
        "/api/admin/system-health",
        "/api/system/status"
    ]

    for ep in endpoints:
        res = client.get(ep, headers=headers)
        assert res.status_code == 403, f"Expected 403 Forbidden for regular user request to {ep}, got {res.status_code}"


@pytest.mark.asyncio
async def test_admin_rbac_super_admin_authorized():
    """Authenticated SUPER_ADMIN requests to admin endpoints must return 200 OK."""
    await init_db()

    # Seed super admin user into DB
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserModel).where(UserModel.id == 8801))
        admin_user = res.scalars().first()
        if not admin_user:
            admin_user = UserModel(
                id=8801,
                username="admin_rbac_test",
                email="jiodkd@gmail.com",
                password_hash="hash123",
                role="SUPER_ADMIN"
            )
            session.add(admin_user)
            await session.commit()

    token = create_access_token({"sub": "8801", "email": "jiodkd@gmail.com"})
    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        "/api/admin/users",
        "/api/admin/tenants",
        "/api/admin/revenue",
        "/api/admin/platform-metrics",
        "/api/admin/system-health"
    ]

    for ep in endpoints:
        res = client.get(ep, headers=headers)
        assert res.status_code == 200, f"Expected 200 OK for super admin request to {ep}, got {res.status_code}"
