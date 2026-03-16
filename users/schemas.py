from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    mobile: str
    password: str
    gender: str
    city: str

class UserUpdate(BaseModel):
    fullname: str
    email: EmailStr
    mobile: str
    gender: str
    city: str

class UserResponse(BaseModel):
    user_id: int
    fullname: str
    email: str
    mobile: str
    gender: str
    city: str
    created_at: str
    updated_at: str
