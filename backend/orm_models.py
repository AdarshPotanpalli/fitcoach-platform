from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .database import Base
from datetime import datetime

class Users(Base):
    __tablename__ = "users"
    
    email = Column(String, unique= True, nullable= False, primary_key= True)
    username = Column(String, nullable= False)
    password = Column(String, unique= True, nullable= False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Preferences(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, unique=True, nullable=False, primary_key= True, autoincrement=True)
    goal = Column(String, nullable= False)
    level = Column(String, nullable= False) 
    lifestyle = Column(String, nullable= False)
    preferred_timings = Column(String, nullable= False)
    
class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, unique=True, nullable=False, primary_key= True, autoincrement=True)
    task1_done = Column(Boolean, nullable=False)
    task2_done = Column(Boolean, nullable=False)
    task3_done = Column(Boolean, nullable=False)

# for logout we need to blacklist tokens, 
# to store the blacklisted tokens we are creating this table    
class BlacklistedTokens(Base):
    __tablename__ = "blacklistedtokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    email = Column(String, nullable=False)  # Optional: track who logged out