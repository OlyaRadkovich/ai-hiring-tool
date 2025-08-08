from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class UserInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    company: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    company: str
    is_active: bool
    created_at: datetime
