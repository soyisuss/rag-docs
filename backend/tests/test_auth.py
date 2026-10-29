import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from src.presentation.main import create_app


@pytest.mark.anyio
async def test_register_user_success():
    unique_email = f"user_{uuid.uuid4().hex[:8]}@ejemplo.com"
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "email": unique_email,
            "password": "Password123!"
        }
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == unique_email
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data


@pytest.mark.anyio
async def test_register_user_duplicate_email_conflict():
    duplicate_email = "usuario_duplicado@ejemplo.com"
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "email": duplicate_email,
            "password": "Password123!"
        }
        # Primer intento (se asegura que existe)
        first_resp = await client.post("/api/v1/auth/register", json=payload)
        assert first_resp.status_code in (201, 409)

        # Segundo intento con el mismo email -> debe rechazar con 409
        second_resp = await client.post("/api/v1/auth/register", json=payload)
        assert second_resp.status_code == 409
        data = second_resp.json()
        assert "ya se encuentra registrado" in data.get("detail", "")


@pytest.mark.anyio
async def test_register_user_invalid_payload():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Email sin formato válido
        invalid_email_resp = await client.post(
            "/api/v1/auth/register", 
            json={"email": "no-es-correo", "password": "Password123!"}
        )
        assert invalid_email_resp.status_code == 422

        # Contraseña vacía o menor a 6 caracteres
        short_pwd_resp = await client.post(
            "/api/v1/auth/register", 
            json={"email": "valido@ejemplo.com", "password": "123"}
        )
        assert short_pwd_resp.status_code == 422
