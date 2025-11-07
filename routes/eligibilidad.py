from fastapi import APIRouter, HTTPException
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@router.get("/usuarios/{usuario_id}")
async def verificar_elegibilidad(usuario_id: int):
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT elegible FROM usuarios WHERE id = $1", usuario_id
            )

            if not result:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            return {"elegible": result["elegible"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar elegibilidad: {str(e)}")
