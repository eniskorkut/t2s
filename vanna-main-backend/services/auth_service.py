"""
Auth Service - Single Responsibility: Authentication and password management.
SOLID: Single Responsibility Principle
"""
import sqlite3
import bcrypt
from typing import Optional, Dict
from .database_service import DatabaseService


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
        query = "SELECT id, email, password_hash FROM users WHERE email = ?"
        results = self.db_service.execute_query(query, (email,))
        
        if not results:
            return None
        
        user = results[0]
        
        if self.verify_password(password, user['password_hash']):
            # Remove password hash from returned user data
            return {
                'id': user['id'],
                'email': user['email']
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
        
        # Create new user
        password_hash = self.hash_password(password)
        insert_query = """
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
        """
        
        try:
            user_id = self.db_service.execute_insert(
                insert_query,
                (email, password_hash)
            )
            return user_id
        except sqlite3.IntegrityError:
            return None
