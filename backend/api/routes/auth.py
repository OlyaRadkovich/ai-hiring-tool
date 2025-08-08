from fastapi import APIRouter
from pydantic import BaseModel, EmailStr


router = APIRouter(tags=["auth"], prefix="/auth")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict:
    return {
        "token": "dummy-token",
        "user": {"email": payload.email, "name": "John Doe"},
    }


@router.post("/register")
def register(payload: LoginRequest) -> dict:
    return {
        "token": "dummy-token",
        "user": {"email": payload.email, "name": "John Doe"},
    }


