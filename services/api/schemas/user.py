from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = None
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True  # enables ORM mode in Pydantic v2
