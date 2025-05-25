from pydantic import BaseModel, EmailStr
from datetime import datetime

class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str

class CreateUserResponse(BaseModel):
    email: EmailStr
    username: str
    created_at: datetime
    
    class Config: # setting the compatibility of return of an endpoint
        from_attributes = True