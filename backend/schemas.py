from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CreateUser(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3)
    password: str

class CreateUserResponse(BaseModel):
    email: EmailStr
    username: str
    created_at: datetime
    
    class Config: # setting the compatibility of return of an endpoint
        from_attributes = True

class LoginUser(BaseModel):
    email: EmailStr
    password: str    
    
class TokenData(BaseModel):
    email: str | None = None