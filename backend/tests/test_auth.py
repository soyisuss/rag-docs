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


@pytest.mark.anyio
async def test_login_user_success():
    unique_email = f"login_user_{uuid.uuid4().hex[:8]}@ejemplo.com"
    raw_password = "SecretPassword123!"
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Registrar usuario primero
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": raw_password}
        )
        assert reg_resp.status_code == 201

        # Iniciar sesión
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": raw_password}
        )
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == unique_email
        assert "id" in data["user"]


@pytest.mark.anyio
async def test_login_user_invalid_credentials():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Caso 1: Correo inexistente
        resp_no_user = await client.post(
            "/api/v1/auth/login",
            json={"email": "usuario_fantasma_no_existe@ejemplo.com", "password": "Password123!"}
        )
        assert resp_no_user.status_code == 401
        assert "Credenciales inválidas" in resp_no_user.json().get("detail", "")

        # Caso 2: Correo existente pero contraseña incorrecta
        user_email = f"user_wrong_pw_{uuid.uuid4().hex[:8]}@ejemplo.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": user_email, "password": "PasswordCorrecta123!"}
        )
        resp_wrong_pw = await client.post(
            "/api/v1/auth/login",
            json={"email": user_email, "password": "PasswordEquivocada999"}
        )
        assert resp_wrong_pw.status_code == 401
        assert "Credenciales inválidas" in resp_wrong_pw.json().get("detail", "")


@pytest.mark.anyio
async def test_login_user_invalid_payload():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Email sin formato válido
        invalid_email_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "no-es-correo", "password": "Password123!"}
        )
        assert invalid_email_resp.status_code == 422

        # Contraseña vacía
        empty_pwd_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "usuario@ejemplo.com", "password": ""}
        )
        assert empty_pwd_resp.status_code == 422



