from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends
from .. import utils, database, schemas, orm_models

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