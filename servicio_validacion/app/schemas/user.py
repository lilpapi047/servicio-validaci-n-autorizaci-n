from pydantic import BaseModel, EmailStr, constr, Field, field_validator
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Debe contener al menos una mayúscula y un número")
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    date_of_birth: str
    country_code: str | None = None
    phone: str | None = None

    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe tener al menos una letra mayúscula.")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe tener al menos un número.")
        return value

    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "Segura123"
            }
        }
