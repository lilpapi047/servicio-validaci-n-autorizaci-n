from pydantic import BaseModel, EmailStr, constr

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)