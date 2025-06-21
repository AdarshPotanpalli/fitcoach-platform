from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2
from typing import Annotated
from fastapi.responses import StreamingResponse
import json

router = APIRouter(
    prefix= "/coach",
    tags = ["Coach"]
)

@router.post("")
async def stream_chat(
    current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)],
    query: schemas.UserQuery,
    db: Session = Depends(database.get_db)
    ):
    """get the streaming response from the chatbot if the user has a plan."""
    
    user_id = current_user.email
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
    if not user_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plans found for user {current_user.username}."
        )
    return StreamingResponse(
        content = utils.get_chatbot_response(query.user_query, user_id, str(user_plans.task1_content+ 
                                                                  user_plans.task2_content+ 
                                                                  user_plans.task3_content)),
        media_type="text/plain"
    )