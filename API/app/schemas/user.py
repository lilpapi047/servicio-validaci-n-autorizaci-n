from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr, field_validator
import re


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    phone: Optional[str] = None


class UserRegister(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Debe contener al menos una mayúscula y un número",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe tener al menos una letra mayúscula.")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe tener al menos un número.")
        return value

    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "Segura123",
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    id: int

    class Config:
        # pydantic v1:
        orm_mode = True
        # si usas pydantic v2, puedes cambiar a:
        # from_attributes = True
