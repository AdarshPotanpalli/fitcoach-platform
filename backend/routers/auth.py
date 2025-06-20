from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2
from typing import Annotated

router = APIRouter(
    prefix= "/auth",
    tags = ["Auth"]
)

@router.post("/register", status_code= status.HTTP_201_CREATED, response_model = schemas.CreateUserResponse)
def create_user(user: schemas.CreateUser, db: Session = Depends(database.get_db)):
    
    """Checks if the user with the given email already exists.
    If not, it hashes the password and creates a new user in the database.
    """
    
    # hashing the password
    hash_password = utils.hash(user.password)
    
    user_query = db.query(orm_models.Users).filter(orm_models.Users.email == user.email).first()
    if user_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists!")
    
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
    
    """Checks if the user with the given email already exists.
    If yes, it verifies the password.
    If the credentials are valid, it generates a JWT token.
    """
    
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

@router.post("/logout")
async def logout(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)], 
                 token: str = Depends(oauth2.oauth2_scheme), 
                 db: Session = Depends(database.get_db)):
    
    """Checks if the token is already blacklisted.
    If not, it adds the token to the blacklist"""
    
    # raise exception if the token you want to blacklist is already blacklisted
    existing_token = db.query(orm_models.BlacklistedTokens).filter(orm_models.BlacklistedTokens.token == token).first()
    if existing_token:
        raise HTTPException(status_code=400, detail="Token is already blacklisted")
    
    #add the blacklisted token to the database
    blacklisted_token = orm_models.BlacklistedTokens(
        token = token,
        email = current_user.email
    )
    db.add(blacklisted_token)
    db.commit()
    return {"detail": "Successfully logged out"}