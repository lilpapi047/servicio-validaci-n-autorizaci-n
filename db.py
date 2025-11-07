import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de .env

DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_NAME = os.getenv("DB_NAME", "sigma")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "sigma")
DATABASE_PORT = int(os.getenv("DB_PORT", 5432))

pool = None  # Pool global

async def init_db_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            user=DATABASE_USER,
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
    return pool
