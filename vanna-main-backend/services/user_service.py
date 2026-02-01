"""
User Service - Single Responsibility: User management.
SOLID: Single Responsibility Principle
"""
from typing import Optional, Dict
from src.db import prisma

class UserService:
    """Service for handling user operations using Prisma."""
    
    def __init__(self):
        """Initialize user service."""
        pass
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        user = await prisma.user.find_unique(
            where={'id': user_id}
        )
        
        if user:
            return {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at
            }
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        user = await prisma.user.find_unique(
            where={'email': email}
        )
        
        if user:
            return {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at
            }
        return None

    async def get_all_users(self) -> list:
        """Get all users."""
        users = await prisma.user.find_many(
            order={'created_at': 'desc'}
        )
        return [
            {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at
            }
            for user in users
        ]

    async def update_user_role(self, user_id: int, role: str) -> bool:
        """Update a user's role."""
        try:
            await prisma.user.update(
                where={'id': user_id},
                data={'role': role}
            )
            return True
        except Exception:
            return False
