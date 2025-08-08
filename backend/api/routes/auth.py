from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from backend.api.models import AuthResponse
from backend.api.deps import get_auth_service
from backend.services.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    company: str

@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Login endpoint"""
    result = await auth_service.authenticate_user(payload.email, payload.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return result

@router.post("/register", response_model=AuthResponse)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Register endpoint"""
    try:
        return await auth_service.register_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.firstName,
            last_name=payload.lastName,
            company=payload.company
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


