from fastapi import FastAPI, status, HTTPException, Depends
from .routers import auth, preferences, plans
from . import orm_models, database, schemas, oauth2
from typing import Annotated

orm_models.Base.metadata.create_all(database.engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(preferences.router)
app.include_router(plans.router)

# app route to get the current user
@app.get("/me", response_model=schemas.CreateUserResponse, status_code=status.HTTP_200_OK)
def get_user(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)]):
    return current_user
    
