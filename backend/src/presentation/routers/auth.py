import os
import datetime
import jwt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import bcrypt
from src.infrastructure.database import get_db_pool

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "yael-bot-jwt-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


class RegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: int
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not configured")

    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async with pool.acquire() as conn:
        existing = await conn.fetchval("SELECT id FROM users WHERE email = $1", payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")

        row = await conn.fetchrow(
            "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email",
            payload.email,
            hashed,
        )
        return UserResponse(id=row["id"], email=row["email"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(status_code=500, detail="Database not configured")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, email, password_hash FROM users WHERE email = $1", payload.email)
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

        valid_password = bcrypt.checkpw(payload.password.encode("utf-8"), row["password_hash"].encode("utf-8"))
        if not valid_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

        token_payload = {
            "sub": str(row["id"]),
            "email": row["email"],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(id=row["id"], email=row["email"]),
        )
