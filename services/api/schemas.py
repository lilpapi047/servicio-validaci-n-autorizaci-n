from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = Field(None, max_length=2)
    phone: Optional[str] = None
    
    @field_validator('country_code', mode='before')
    def validate_country_code(cls, v):
        if v:
            v = v.strip()
            if len(v) != 2:
                raise ValueError('country_code debe tener exactamente 2 caracteres (ej: CO, MX, US)')
        return v if v else None

class UserCreate(UserBase):
    hash_pwd: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = Field(None, max_length=2)
    phone: Optional[str] = None
    email: Optional[str] = None
    
    @field_validator('country_code', mode='before')
    def validate_country_code(cls, v):
        if v:
            v = v.strip()
            if len(v) != 2:
                raise ValueError('country_code debe tener exactamente 2 caracteres (ej: CO, MX, US)')
        return v if v else None

class UserChangePassword(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def passwords_match(cls, m):
        if m.new_password != m.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        return m

class UserResponse(UserBase):
    id: int
    is_verified: bool
    is_2fa_enabled: Optional[bool]
    email_verified_at: Optional[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    country_code: Optional[str]
    phone: Optional[str]
    is_verified: bool
    is_2fa_enabled: Optional[bool]
    email_verified_at: Optional[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)
