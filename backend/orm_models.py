from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Date, text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class Users(Base):
    __tablename__ = "users"
    
    email = Column(String, unique= True, nullable= False, primary_key= True)
    username = Column(String, nullable= False)
    password = Column(String, unique= True, nullable= False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # setting the relationship
    preferences = relationship("Preferences", back_populates="owner")
    feedback = relationship("Feedback", back_populates="owner")
    plans = relationship("Plans", back_populates="owner")
    
## Preferences to be set by the user
class Preferences(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, unique=True, nullable=False, primary_key= True, autoincrement=True)
    goal = Column(String, nullable= False)
    lifestyle = Column(String, nullable= False)
    preferred_timings = Column(ARRAY(String), nullable= False)
    note = Column(String)
    
    # setting the foreign key
    owner_email = Column(String, ForeignKey("users.email", ondelete= "CASCADE"), nullable= False)
    owner = relationship("Users", back_populates="preferences")
    
## Daily Feedback to be given by the user    
class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, unique=True, nullable=False, primary_key= True, autoincrement=True)
    task1_done = Column(Boolean, server_default=text("false"))
    task2_done = Column(Boolean, server_default= text("false"))
    task3_done = Column(Boolean, server_default= text("false"))
    date = Column(Date, nullable = False)
    
    # setting the foregin key
    owner_email = Column(String, ForeignKey("users.email", ondelete= "CASCADE"), nullable= False)
    owner = relationship("Users", back_populates="feedback")

# for logout we need to blacklist tokens, 
# to store the blacklisted tokens we are creating this table    
class BlacklistedTokens(Base):
    __tablename__ = "blacklistedtokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    email = Column(String, nullable=False)  # Optional: track who logged out
    
## Daily tasks for the user
class Plans(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, unique=True, nullable=False, primary_key= True, autoincrement=True)
    task1_title = Column(String, nullable= False)
    task1_content = Column(String, nullable= False)
    task2_title = Column(String, nullable= False)
    task2_content = Column(String, nullable= False)
    task3_title = Column(String, nullable= False)
    task3_content = Column(String, nullable= False)
    
    # setting the foregin key
    owner_email = Column(String, ForeignKey("users.email", ondelete= "CASCADE"), nullable= False)
    owner = relationship("Users", back_populates="plans")
    