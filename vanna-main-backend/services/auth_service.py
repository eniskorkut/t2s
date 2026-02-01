"""
Auth Service - Single Responsibility: Authentication and password management.
SOLID: Single Responsibility Principle
"""
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt
from src.db import prisma
from prisma.models import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "vanna-t2s-secure-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

class AuthService:
    """Service for handling authentication operations using Prisma."""
    
    def __init__(self):
        """Initialize auth service."""
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    async def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate a user by email and password."""
        user = await prisma.user.find_unique(
            where={'email': email}
        )
        
        if not user:
            return None
        
        if self.verify_password(password, user.password_hash):
            return {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        
        return None
    
    async def create_user(self, email: str, password: str) -> Optional[int]:
        """Create a new user."""
        # Check if user already exists
        existing = await prisma.user.find_unique(where={'email': email})
        
        if existing:
            return None
        
        # Check if this is the first user
        count = await prisma.user.count()
        role = 'admin' if count == 0 else 'user'
        
        # Create new user
        password_hash = self.hash_password(password)
        
        try:
            user = await prisma.user.create(
                data={
                    'email': email,
                    'password_hash': password_hash,
                    'role': role
                }
            )
            return user.id
        except Exception:
            return None

    async def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user password."""
        # Check if user exists
        user = await prisma.user.find_unique(where={'email': email})
        
        if not user:
            return False
            
        password_hash = self.hash_password(new_password)
        
        await prisma.user.update(
            where={'email': email},
            data={'password_hash': password_hash}
        )
        
        return True

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a new access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_reset_token(self, email: str) -> str:
        """Create a password reset token (valid for 15 minutes)."""
        data = {
            "sub": email,
            "type": "reset"
        }
        expires_delta = timedelta(minutes=15)
        return self.create_access_token(data, expires_delta)

    def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "reset":
                return None
            return payload.get("sub")
        except jwt.JWTError:
            return None

