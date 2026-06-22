from pydantic import BaseModel, EmailStr

# What we expect from the user when they register
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# What we send back to the user (Notice we NEVER send the password back!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

# The Token structure
class Token(BaseModel):
    access_token: str
    token_type: str