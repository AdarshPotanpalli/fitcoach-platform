from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import List, Optional, Dict

class CreateUser(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3)
    password: str

class CreateUserResponse(BaseModel):
    email: EmailStr
    username: str
    created_at: datetime
    is_google_synced: bool = False
    date_last_synced: Optional[date] = None
    
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

class FeedbackOut(Feedback):
    list_of_task_failures: List
    list_of_task_successes: List
    date: date    


class UserExperience(BaseModel):
    experience_rating: int = Field(ge=1, le=5)  # Rating from 1 to 5
    experience_comments: Optional[str] = None  # Optional comments about the experience
    
# the user query input for the chatbot
class UserQuery(BaseModel):
    user_query: str