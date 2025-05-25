from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash(raw_password:str):
    """Hash a raw password"""
    return pwd_context.hash(raw_password)

def verify(raw_password: str, hashed_password:str):
    """Verify if the entered raw password mathes the hashed password"""
    return pwd_context.verify(secret= raw_password, hash = hashed_password)