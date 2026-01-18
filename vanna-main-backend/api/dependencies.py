"""
FastAPI dependencies for dependency injection
Following Dependency Inversion Principle - High-level modules depend on abstractions
Following Single Responsibility Principle - Only handles dependency injection
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services import DatabaseService, AuthService, UserService, QueryService, ChatService

security = HTTPBearer(auto_error=False)


def get_db_service(request: Request) -> DatabaseService:
    """Get database service from app state."""
    return request.app.state.db_service


def get_auth_service(request: Request) -> AuthService:
    """Get auth service from app state."""
    return request.app.state.auth_service


def get_user_service(request: Request) -> UserService:
    """Get user service from app state."""
    return request.app.state.user_service


def get_query_service(request: Request) -> QueryService:
    """Get query service from app state."""
    return request.app.state.query_service


def get_chat_service(request: Request) -> ChatService:
    """Get chat service from app state."""
    return request.app.state.chat_service


def get_vanna_instance(request: Request):
    """Get Vanna instance from app state."""
    return request.app.state.vanna_instance


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    """
    Get current authenticated user.
    Uses cookie-based authentication for session management.
    Following Single Responsibility Principle - Only handles user authentication
    """
    # Cookie-based auth - get user_id from cookie
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_id = int(user_id)
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
