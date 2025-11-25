from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.api.schemas import UserCreate, UserUpdate, UserChangePassword, UserProfileResponse, UserResponse
from services.api.crud import (
    get_user_by_id, 
    get_user_by_email,
    create_user, 
    update_user_profile, 
    change_password, 
    delete_user
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/registro", tags=["Perfil"])
def registrar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    try:
        # Verificar si el email ya existe
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya esta registrado")
        
        # Crear usuario
        new_user = create_user(db, user)
        return {
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "is_verified": new_user.is_verified,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al registrar usuario")

@router.get("/perfil/{user_id}", tags=["Perfil"])
def obtener_perfil(user_id: int, db: Session = Depends(get_db)):
    """Obtener perfil del usuario"""
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "country_code": user.country_code,
            "phone": user.phone,
            "is_verified": user.is_verified,
            "is_2fa_enabled": user.is_2fa_enabled,
            "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener perfil")

@router.put("/perfil/{user_id}", tags=["Perfil"])
def actualizar_perfil(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Actualizar perfil del usuario"""
    try:
        # Verificar que el usuario existe
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Si intenta cambiar email, verificar que no exista otro con ese email
        if user_update.email and user_update.email != user.email:
            existing_user = get_user_by_email(db, user_update.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="El email ya esta en uso")
        
        # Actualizar perfil
        updated_user = update_user_profile(db, user_id, user_update)
        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "date_of_birth": updated_user.date_of_birth.isoformat() if updated_user.date_of_birth else None,
            "country_code": updated_user.country_code,
            "phone": updated_user.phone,
            "is_verified": updated_user.is_verified,
            "is_2fa_enabled": updated_user.is_2fa_enabled,
            "email_verified_at": updated_user.email_verified_at.isoformat() if updated_user.email_verified_at else None,
            "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando perfil: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar perfil")

@router.post("/perfil/{user_id}/cambiar-password", tags=["Perfil"])
def cambiar_contrasena(user_id: int, password_change: UserChangePassword, db: Session = Depends(get_db)):
    """Cambiar contrasena del usuario"""
    try:
        # Verificar que el usuario existe
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Cambiar contrasena
        success = change_password(db, user_id, password_change)
        if not success:
            raise HTTPException(status_code=401, detail="Contrasena anterior incorrecta")
        
        return {"mensaje": "Contrasena cambiada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando contrasena: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cambiar contrasena")

@router.delete("/perfil/{user_id}", tags=["Perfil"])
def eliminar_cuenta(user_id: int, db: Session = Depends(get_db)):
    """Eliminar cuenta del usuario"""
    try:
        # Verificar que el usuario existe
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Eliminar usuario
        success = delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=500, detail="No se pudo eliminar la cuenta")
        
        return {"mensaje": "Cuenta eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando cuenta: {str(e)}")
        error_msg = str(e)
        if "foreign key" in error_msg.lower() or "constraint" in error_msg.lower():
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar la cuenta porque tiene registros asociados en el sistema"
            )
        raise HTTPException(status_code=500, detail="Error al eliminar cuenta")

@router.get("/usuarios", tags=["Perfil"])
def listar_usuarios(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Listar todos los usuarios (con paginacion)"""
    try:
        from services.api.models import User
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "country_code": u.country_code,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    except Exception as e:
        logger.error(f"Error listando usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al listar usuarios")
