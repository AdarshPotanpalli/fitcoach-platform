from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# DATABASE_URL = "postgresql://<username>:<password>@<ip_address/host_name>:<port_name>/<database_name>")
DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_IP}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
Session_local = sessionmaker(bind= engine, autoflush= False)

Base = declarative_base()

def get_db():
    db = Session_local()
    try:
        yield db #yields the database session and pauses also closes the session on next call
    finally:
        db.close()
