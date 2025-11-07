from fastapi import APIRouter, HTTPException
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_pool():
    return await asyncpg.create_pool(DATABASE_URL)


@router.post("/asignar/{usuario_id}")
async def asignar_boleto(usuario_id: int):
    max_intentos = 3
    intento = 0

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            while intento < max_intentos:
                try:
                    await conn.execute(
                        "INSERT INTO boletos (usuario_id, asignado) VALUES ($1, TRUE)",
                        usuario_id,
                    )
                    return {"mensaje": "Boleto asignado correctamente"}
                except Exception as e:
                    intento += 1
                    print(f"Intento {intento} falló: {str(e)}")
                    if intento >= max_intentos:
                        raise HTTPException(
                            status_code=500,
                            detail="Error persistente: no se pudo asignar el boleto",
                        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la conexión: {str(e)}")
