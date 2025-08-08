from typing import Optional
from bson import ObjectId
from backend.database.connection import get_database
from backend.models.user import UserInDB, UserCreate, UserResponse
import bcrypt

class UserRepository:
    def __init__(self):
        self.database = get_database()
        self.collection = self.database.users

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        """Create a new user with hashed password."""
        # Check if user already exists
        existing_user = await self.collection.find_one({"email": user_create.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user_create.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user document
        user_data = user_create.model_dump()
        user_data.pop('password')
        user_data['hashed_password'] = hashed_password
        
        result = await self.collection.insert_one(user_data)
        
        # Get created user
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(created_user["_id"]),
            email=created_user["email"],
            first_name=created_user["first_name"],
            last_name=created_user["last_name"],
            company=created_user["company"],
            is_active=created_user["is_active"],
            created_at=created_user["created_at"]
        )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            # Convert ObjectId to string for Pydantic validation
            user_data["id"] = str(user_data["_id"])
            # Remove the original _id field to avoid conflicts
            user_data.pop("_id", None)
            return UserInDB(**user_data)
        return None

    async def verify_password(self, email: str, password: str) -> bool:
        """Verify user password."""
        user = await self.get_user_by_email(email)
        if not user:
            return False
        
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            user.hashed_password.encode('utf-8')
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return UserResponse(
                    id=str(user_data["_id"]),
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    company=user_data["company"],
                    is_active=user_data["is_active"],
                    created_at=user_data["created_at"]
                )
        except Exception:
            pass
        return None
