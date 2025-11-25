from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.elegibilidad.reintento_service import asignar_rifa
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/asignar/{usuario_id}")
def asignar_boleto(usuario_id: int, db: Session = Depends(get_db)):
    """Intenta asignar una rifa a un usuario con reintentos"""
    try:
        resultado = asignar_rifa(usuario_id, intentos=3)
        
        if resultado:
            return {
                "usuario_id": usuario_id,
                "mensaje": "Boleto asignado correctamente",
                "asignado": True
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error persistente: no se pudo asignar el boleto después de 3 intentos"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error asignando boleto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la asignación: {str(e)}")
