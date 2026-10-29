import pytest
import uuid
import jwt
from httpx import AsyncClient, ASGITransport
from src.presentation.main import create_app
from src.infrastructure import config


@pytest.mark.anyio
async def test_protected_routes_unauthorized_without_token():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # GET /api/documents
        resp_docs = await client.get("/api/documents")
        assert resp_docs.status_code == 401
        assert "Autenticación requerida" in resp_docs.json().get("detail", "")

        # POST /api/chat
        resp_chat = await client.post("/api/chat", json={"query": "test"})
        assert resp_chat.status_code == 401
        assert "Autenticación requerida" in resp_chat.json().get("detail", "")

        # DELETE /api/documents/some.pdf
        resp_del = await client.delete("/api/documents/some.pdf")
        assert resp_del.status_code == 401
        assert "Autenticación requerida" in resp_del.json().get("detail", "")


@pytest.mark.anyio
async def test_protected_routes_with_invalid_or_expired_token():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Token malformado
        headers = {"Authorization": "Bearer token-invalido-xyz"}
        resp = await client.get("/api/documents", headers=headers)
        assert resp.status_code == 401
        assert "inválido" in resp.json().get("detail", "")


@pytest.mark.anyio
async def test_protected_routes_authorized_with_valid_token():
    # Creamos un token válido directamente con la clave secreta
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "test_auth_user@ejemplo.com"
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}

    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # GET /api/documents con token debe responder 200
        resp_docs = await client.get("/api/documents", headers=headers)
        assert resp_docs.status_code == 200
        data = resp_docs.json()
        assert "documents" in data
        assert "total" in data
