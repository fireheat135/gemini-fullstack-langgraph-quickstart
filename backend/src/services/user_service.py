"""User service for managing user accounts."""

from typing import Optional

from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


class UserService:
    """Service for managing users."""

    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = User(
            email=user_create.email,
            name=user_create.name,
            hashed_password=hashed_password,
            role=user_create.role,
            company=user_create.company,
            bio=user_create.bio,
            language=user_create.language,
            timezone=user_create.timezone,
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user account."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        db_user.is_active = True
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user account."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        db_user.is_active = False
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def verify_user(self, user_id: int) -> Optional[User]:
        """Verify user account."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        db_user.is_verified = True
        self.db.commit()
        self.db.refresh(db_user)
        return db_user