import pytest
import asyncio
from db import create_pool

@pytest.fixture(scope="session")
async def db_pool():
    pool = await create_pool()
    yield pool
    await pool.close()