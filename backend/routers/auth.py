from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2
from typing import Annotated

router = APIRouter(
    prefix= "/auth",
    tags = ["Auth"]
)

@router.post("/create_user", status_code= status.HTTP_201_CREATED, response_model = schemas.CreateUserResponse)
def create_user(user: schemas.CreateUser, db: Session = Depends(database.get_db)):
    
    # hashing the password
    hash_password = utils.hash(user.password)
    
    # creating the new user and committing changes
    new_user = orm_models.Users(
        email = user.email,
        username = user.username,
        password = hash_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
    
    # check if the user with email id exists
    user_queried = db.query(orm_models.Users).filter(orm_models.Users.email == form_data.username).first()
    if not user_queried:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials!")
    
    # verify the password
    if not utils.verify(form_data.password, user_queried.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials!")
    
    # get jwt token if everything's correct
    jwt_token = oauth2.create_access_token(data = {"email": form_data.username}) # in username actually email is passed
    
    return {"token": jwt_token, "token_type": "bearer"}