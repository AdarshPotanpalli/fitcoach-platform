from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional, Dict

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
    
class Preferences(BaseModel):
    goal: str
    lifestyle: str
    preferred_timings: List[str]
    note: Optional[str] = None
    
class PreferencesOut(Preferences):
    owner_email: str
    
    class Config:
        from_attributes = True
    
class Plans(BaseModel):
    task1_title: str = Field(max_length=50)
    task1_content: str #JSON string with steps
    task1_timings_start: str
    task1_timings_end: str
    task1_tip: str

    task2_title: str = Field(max_length=50)
    task2_content: str
    task2_timings_start: str
    task2_timings_end: str
    task2_tip: str

    task3_title: str = Field(max_length=50)
    task3_content: str
    task3_timings_start: str
    task3_timings_end: str
    task3_tip: str

# if the daily task is done or not    
class Feedback(BaseModel):
    
    task1_done: bool
    task2_done: bool
    task3_done: bool
    
# the user query input for the chatbot
class UserQuery(BaseModel):
    user_query: str