import asyncio
from db import init_db_pool  

async def test_connection():
    try:
        pool = await init_db_pool()
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT 1;")
            print("Conexión exitosa:", result)
    except Exception as e:
        print("Error conectando a la DB:", e)

asyncio.run(test_connection())