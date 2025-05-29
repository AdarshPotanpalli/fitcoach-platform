from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2
from typing import Annotated, List
from datetime import date


router = APIRouter(
    prefix="/plans",
    tags=["Plans"]
)

## GET PLAN ------------------------
@router.get("", response_model=schemas.Plans, status_code= status.HTTP_200_OK)
def get_plan(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
    if not user_plans:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"The plans for {current_user.username} not found!")
    
    return user_plans

## POST PLAN ---------------------------
@router.post("", response_model=schemas.Plans, status_code=status.HTTP_201_CREATED)
def create_plan(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    # Check if user has preferences
    preferences = db.query(orm_models.Preferences).filter(orm_models.Preferences.owner_email == current_user.email).first()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot generate a plan without user preferences."
        )

    # Raise exception if plan already exists
    existing_plan = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A plan for today already exists. Update the plan if you want."
        )

    # Generate plan using preferences
    generated_plan = utils.get_todays_plan(preferences)
    
    # Validate the plan
    try:
        validated_plan = schemas.Plans(**generated_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Generated plan validation failed: {str(e)}"
        )

    # Create and save plan
    new_plan = orm_models.Plans(
        **validated_plan.dict(),
        owner_email = current_user.email
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

## UPDATE PLAN ---------------------------
@router.put("", response_model=schemas.Plans)
def update_plan(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    
    # Check if user has preferences
    preferences = db.query(orm_models.Preferences).filter(orm_models.Preferences.owner_email == current_user.email).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot generate a plan without user preferences."
        )
        
    # check if user has existing plans    
    plan_query = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email)
    if not plan_query.first():
        raise HTTPException(
            status_code=404, 
            detail="No plan found to update."
        )

    # Generate plan using preferences
    generated_plan = utils.get_todays_plan(preferences)
    
    # Validate the plan
    try:
        validated_plan = schemas.Plans(**generated_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Generated plan validation failed: {str(e)}"
        )
    
    plan_query.update(validated_plan.dict(), synchronize_session=False)
    db.commit()
    return plan_query.first()

## DELETE PLAN -------------------------------
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    plan_query = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email)
    
    if not plan_query.first():
        raise HTTPException(status_code=404, detail="No plan found to delete.")

    plan_query.delete(synchronize_session=False)
    db.commit()
    return


## POST FEEDBACK --> if the user has finished the tasks or not
@router.post("/feedback", response_model=schemas.Feedback, status_code= status.HTTP_200_OK)
def post_feedback(
    feedback: schemas.Feedback,
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    db: Session = Depends(database.get_db)
):
    # raise exception if user had no plans
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
    if not user_plans:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"The plans for {current_user.username} not found!")
    
    # check if the user has already given feedback today
    feedback_exists = db.query(orm_models.Feedback).filter(
        orm_models.Feedback.owner_email == current_user.email,
        orm_models.Feedback.date == date.today()
        ).first()
    
    if feedback_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail= f"{current_user.username} has already given feedback today!"
            ) 
        
    user_feedback = orm_models.Feedback(
        **feedback.dict(),
        owner_email = current_user.email,
        date = date.today()
        )
    db.add(user_feedback)
    db.commit()
    db.refresh(user_feedback)
    
    return user_feedback
    