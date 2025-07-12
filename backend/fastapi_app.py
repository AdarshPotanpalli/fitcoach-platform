from fastapi import FastAPI, status, HTTPException, Depends
from .routers import auth, preferences, plans, coach, calendar
from . import orm_models, database, schemas, oauth2, event_scheduler
from typing import Annotated, List
from sqlalchemy.orm import Session

orm_models.Base.metadata.create_all(database.engine)
app = FastAPI()

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
    
