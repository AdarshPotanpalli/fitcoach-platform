from fastapi import FastAPI, status, HTTPException, Depends
from .routers import auth, preferences, plans, coach, calendar
from . import orm_models, database, schemas, oauth2, event_scheduler
from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
orm_models.Base.metadata.create_all(database.engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(preferences.router)
app.include_router(plans.router)
app.include_router(coach.router)
app.include_router(calendar.router)

# app route to get the current user
@app.get("/me", response_model=schemas.CreateUserResponse, status_code=status.HTTP_200_OK)
def get_user(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)]):
    return current_user
    
@app.get("/all_users", response_model=List[schemas.CreateUserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(database.get_db)):
    """Gets all users in the database, this is used by admin"""
    users = db.query(orm_models.Users).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found!")
    return users

@app.post("/user_ratings_comments", status_code=status.HTTP_201_CREATED)
def post_user_ratings_comments(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    ratings: schemas.UserExperience, 
    db: Session = Depends(database.get_db)
):
    """Posts the user ratings and comments about the app"""
    
    current_user.experience_rating = ratings.experience_rating
    current_user.experience_comments = ratings.experience_comments
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Ratings and comments posted successfully!"}

@app.on_event("startup")
def on_startup():
    """Starts the background scheduler to update the plans every day at 6 AM"""
    event_scheduler.start_scheduler()
    
