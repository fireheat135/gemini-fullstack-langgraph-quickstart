"""User service for authentication and user management."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..models.user import User, UserRole


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_multi(
        self, 
        *,
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get multiple users with filtering."""
        query = self.db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()

    def create(self, user_data: Dict[str, Any]) -> User:
        """Create new user."""
        # Hash password if provided
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        db_obj = User(**user_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        *,
        db_obj: User,
        obj_in: Union[Dict[str, Any], Any]
    ) -> User:
        """Update user information."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        # Hash password if updating
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, user_id: int) -> Optional[User]:
        """Soft delete user (set inactive)."""
        obj = self.db.query(User).get(user_id)
        if obj:
            obj.is_active = False
            obj.updated_at = datetime.utcnow()
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login timestamp."""
        user = self.get(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser
    
    def has_permission(self, user: User, required_role: UserRole) -> bool:
        """Check if user has required permission level."""
        return user.has_permission(required_role)
    
    def create_superuser(self, email: str, password: str, name: str) -> User:
        """Create superuser account."""
        user_data = {
            "email": email,
            "name": name,
            "password": password,
            "user_role": UserRole.ADMIN,
            "is_superuser": True,
            "is_active": True,
            "is_verified": True
        }
        return self.create(user_data)

    # Legacy method names for backward compatibility
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID (legacy method)."""
        return self.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (legacy method)."""
        return self.get_by_email(email)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user (legacy method)."""
        return self.authenticate(email=email, password=password)