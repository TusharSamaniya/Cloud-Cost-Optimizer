from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.user_service import get_user_by_email

# This tells FastAPI where our login route is so it can generate the "Authorize" button in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# This creates a fresh database connection for every single web request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# The "Bouncer": Checks the token, decodes it, and finds the user in the database
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Crack open the token using your secret key
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 2. Look up the user by the email stored inside the token
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user