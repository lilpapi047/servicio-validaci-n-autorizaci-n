from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.api.models import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/usuarios/{usuario_id}")
def verificar_elegibilidad(usuario_id: int, db: Session = Depends(get_db)):
    """Verifica si un usuario es elegible"""
    try:
        user = db.query(User).filter(User.id == usuario_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Aquí puedes agregar lógica de elegibilidad
        return {
            "usuario_id": usuario_id,
            "elegible": user.is_verified,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando elegibilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al verificar elegibilidad: {str(e)}")
