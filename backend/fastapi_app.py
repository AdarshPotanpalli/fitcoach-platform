from fastapi import FastAPI
from .routers import auth
from . import orm_models, database

orm_models.Base.metadata.create_all(database.engine)
app = FastAPI()

app.include_router(auth.router)

