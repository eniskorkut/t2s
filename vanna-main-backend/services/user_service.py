"""
User Service - Single Responsibility: User data operations.
SOLID: Single Responsibility Principle
"""
from typing import Optional, Dict
from .database_service import DatabaseService


class UserService:
    """Service for handling user data operations."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize user service.
        
        Args:
            db_service: DatabaseService instance
        """
        self.db_service = db_service
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary or None if not found
        """
        query = "SELECT id, email, created_at FROM users WHERE id = ?"
        results = self.db_service.execute_query(query, (user_id,))
        
        if results:
            return results[0]
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User dictionary or None if not found
        """
        query = "SELECT id, email, created_at FROM users WHERE email = ?"
        results = self.db_service.execute_query(query, (email,))
        
        if results:
            return results[0]
        return None
