from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Annotated
from jose import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from .config import settings
from . import orm_models, database, schemas

# 32 byte Secret key to encode the JWT
# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY  # Use env var in production!

# Algorithm to use for encoding
ALGORITHM = settings.ALGORITHM

# Token expiration time (e.g., 30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # api endopoint to get token

def create_access_token(data: dict):
    """Create a JWT token with passed data and expiration time being encoded."""
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # merges one dictionary to another

    # generate jwt token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    
    """checks if the passed token is valid.
    If valid, returns the corresponding user."""
    
    # if the passed token in header is blacklisted (user has logged out)
    blacklisted_token = db.query(orm_models.BlacklistedTokens).filter(orm_models.BlacklistedTokens.token == token).first()
    if blacklisted_token:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has been revoked",
        headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # decode the token
        payload = jwt.decode(token = token, key = SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email") # get the payload
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email= email) # schema validation
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.query(orm_models.Users).filter(orm_models.Users.email == token_data.email).first()
    if not user:
        raise credentials_exception
    
    return user