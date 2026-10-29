import os
import asyncpg
from typing import Optional

_pool: Optional[asyncpg.Pool] = None
_pool_loop = None


async def get_db_pool() -> Optional[asyncpg.Pool]:
    global _pool, _pool_loop
    import asyncio
    current_loop = asyncio.get_running_loop()
    if _pool is not None and _pool_loop != current_loop:
        _pool = None

    if _pool is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return None
        _pool = await asyncpg.create_pool(dsn=db_url, min_size=1, max_size=5)
        _pool_loop = current_loop
        async with _pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
    return _pool


async def close_db_pool() -> None:
    global _pool, _pool_loop
    if _pool:
        await _pool.close()
        _pool = None
        _pool_loop = None
