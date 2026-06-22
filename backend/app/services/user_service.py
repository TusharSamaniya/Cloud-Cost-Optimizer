from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def get_user_by_email(db: Session, email: str):
    # This translates to: SELECT * FROM users WHERE email = ? LIMIT 1
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    # 1. Hash the incoming password
    hashed_pw = hash_password(user.password)
    
    # 2. Create the Database object
    db_user = User(email=user.email, hashed_password=hashed_pw)
    
    # 3. Save it to PostgreSQL
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user