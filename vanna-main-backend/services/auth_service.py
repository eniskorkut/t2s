"""
Auth Service - Single Responsibility: Authentication and password management.
SOLID: Single Responsibility Principle
"""
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt
from .database_service import DatabaseService

# Configuration
SECRET_KEY = "vanna-t2s-secure-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize auth service.
        
        Args:
            db_service: DatabaseService instance
        """
        self.db_service = db_service
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user by email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User dictionary if authentication successful, None otherwise
        """
        query = "SELECT id, email, password_hash, role FROM users WHERE email = ?"
        results = self.db_service.execute_query(query, (email,))
        
        if not results:
            return None
        
        user = results[0]
        
        if self.verify_password(password, user['password_hash']):
            # Remove password hash from returned user data
            return {
                'id': user['id'],
                'email': user['email'],
                'role': user['role']
            }
        
        return None
    
    def create_user(self, email: str, password: str) -> Optional[int]:
        """
        Create a new user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User ID if successful, None if email already exists
        """
        # Check if user already exists
        check_query = "SELECT id FROM users WHERE email = ?"
        existing = self.db_service.execute_query(check_query, (email,))
        
        if existing:
            return None
        
        # Check if this is the first user
        count_query = "SELECT count(*) as count FROM users"
        count_result = self.db_service.execute_query(count_query)
        role = 'admin' if count_result[0]['count'] == 0 else 'user'
        
        # Create new user
        password_hash = self.hash_password(password)
        insert_query = """
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
        """
        
        try:
            user_id = self.db_service.execute_insert(
                insert_query,
                (email, password_hash, role)
            )
            return user_id
        except sqlite3.IntegrityError:
            return None

    def reset_password(self, email: str, new_password: str) -> bool:
        """
        Reset user password.
        
        Args:
            email: User email
            new_password: New password
            
        Returns:
            True if successful, False if user not found
        """
        # Check if user exists
        query = "SELECT id FROM users WHERE email = ?"
        results = self.db_service.execute_query(query, (email,))
        
        if not results:
            return False
            
        password_hash = self.hash_password(new_password)
        update_query = "UPDATE users SET password_hash = ? WHERE email = ?"
        
        row_count = self.db_service.execute_update(
            update_query,
            (password_hash, email)
        )
        
        return row_count > 0

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new access token.
        
        Args:
            data: Data to encode in token (payload)
            expires_delta: Expiration time delta
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
