import time
from typing import Optional
from backend.api.models import AuthResponse, UserInfo
from backend.repositories.user_repository import UserRepository
from backend.models.user import UserCreate

class AuthService:
    """Service responsible for authentication business logic"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        # Keep test credentials for demo
        self._valid_credentials = {
            "test@example.com": "password"
        }
    
    async def authenticate_user(self, email: str, password: str) -> Optional[AuthResponse]:
        """Authenticate user with email and password"""
        # First try to verify with database
        if await self.user_repository.verify_password(email, password):
            user = await self.user_repository.get_user_by_email(email)
            return AuthResponse(
                message="Login successful",
                token="fake-jwt-token",  # In real app, generate JWT
                user=UserInfo(email=user.email, firstName=user.first_name)
            )
        
        # Fallback to test credentials for demo
        if email in self._valid_credentials and self._valid_credentials[email] == password:
            return AuthResponse(
                message="Login successful (demo mode)",
                token="fake-jwt-token",
                user=UserInfo(email=email)
            )
        
        return None
    
    async def register_user(self, email: str, password: str, first_name: str, 
                          last_name: str, company: str) -> AuthResponse:
        """Register new user"""
        try:
            user_create = UserCreate(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                company=company
            )
            
            user = await self.user_repository.create_user(user_create)
            
            return AuthResponse(
                message="Registration successful",
                token="fake-jwt-token",  # In real app, generate JWT
                user=UserInfo(email=user.email, firstName=user.first_name)
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")
