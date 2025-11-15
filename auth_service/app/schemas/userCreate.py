from pydantic import BaseModel, EmailStr, Field
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    country_code: str | None = Field(None, min_length=2, max_length=2)
    phone: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True