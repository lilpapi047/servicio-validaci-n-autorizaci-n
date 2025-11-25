import hashlib
from sqlalchemy.orm import Session
from services.api.models import User
from services.api.schemas import UserCreate, UserUpdate, UserChangePassword

def hash_password(password: str) -> str:
    """Hashear una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hash_pwd: str) -> bool:
    """Verificar una contraseña contra su hash"""
    return hash_password(password) == hash_pwd

def get_user_by_id(db: Session, user_id: int) -> User:
    """Obtener usuario por ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User:
    """Obtener usuario por email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Crear nuevo usuario"""
    db_user = User(
        email=user.email,
        hash_pwd=hash_password(user.hash_pwd),
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth,
        country_code=user.country_code,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """Actualizar perfil del usuario"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(db: Session, user_id: int, password_change: UserChangePassword) -> bool:
    """Cambiar contraseña del usuario"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # Verificar contraseña anterior
    if not verify_password(password_change.old_password, db_user.hash_pwd):
        return False
    
    # Actualizar contraseña
    db_user.hash_pwd = hash_password(password_change.new_password)
    db.add(db_user)
    db.commit()
    return True

def delete_user(db: Session, user_id: int) -> bool:
    """Eliminar cuenta del usuario"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True
