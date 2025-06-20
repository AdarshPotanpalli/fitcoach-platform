from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2
from typing import Annotated, List


router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"]
)

## GET PREFERENCES
@router.get("", response_model=schemas.PreferencesOut, status_code=status.HTTP_200_OK)
def get_preferences(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """First checks if the user has preferences set,
    if yes, returns the preferences"""
    
    user_preferences = db.query(orm_models.Preferences).filter(
        orm_models.Preferences.owner_email == current_user.email
    ).first()
    
    # raise exception if the user has no preferences selected
    if not user_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No preferences found for user '{current_user.username}'."
        )

    return user_preferences

# POST PREFERENCES
@router.post("", response_model=schemas.PreferencesOut, status_code=status.HTTP_201_CREATED)
def create_preferences(
    preferences: schemas.Preferences,
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """First checks if the user has preferences set,
    if not, creates new preferences for the user."""
    
    # Check if preferences already exist
    existing = db.query(orm_models.Preferences).filter(
        orm_models.Preferences.owner_email == current_user.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferences already exist. Use PUT to update them."
        )

    # create new Preferences object and then add that to table
    new_preferences = orm_models.Preferences(
        goal=preferences.goal,
        lifestyle=preferences.lifestyle,
        preferred_timings=preferences.preferred_timings,
        note=preferences.note,
        owner_email=current_user.email
    )

    db.add(new_preferences)
    db.commit()
    db.refresh(new_preferences)
    return new_preferences

# UPDATE PREFERENCES
@router.put("", response_model=schemas.PreferencesOut, status_code=status.HTTP_200_OK)
def update_preferences(
    preferences: schemas.Preferences,
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    user_preferences_query = db.query(orm_models.Preferences).filter(
        orm_models.Preferences.owner_email == current_user.email
    )

    # raise exception if the user has no preferences selected
    if not user_preferences_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No preferences found to update. Use POST to create them."
        )

    user_preferences_query.update(preferences.dict(), synchronize_session=False)
    db.commit()
    return user_preferences_query.first()

