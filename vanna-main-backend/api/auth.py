"""
Authentication routes
Following Single Responsibility Principle - Only handles auth endpoints
Following Dependency Inversion Principle - Depends on service abstractions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.schemas import LoginRequest, RegisterRequest, LoginResponse, UserResponse, ResetPasswordRequest, Token
from api.dependencies import get_auth_service, get_user_service, get_current_user
from services import AuthService, UserService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login endpoint.
    Returns JWT access token.
    """
    user = auth_service.authenticate(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user['id']), "role": user['role']}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user['role']
    }


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register endpoint."""
    if len(register_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    user_id = auth_service.create_user(register_data.email, register_data.password)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # Create response with user data
    response = JSONResponse(
        content=LoginResponse(
            success=True,
            user=UserResponse(id=user_id, email=register_data.email)
        ).model_dump(),
        status_code=status.HTTP_201_CREATED
    )
    
    # Set cookie for session management
    response.set_cookie(
        key="user_id",
        value=str(user_id),
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response


@router.post("/logout")
async def logout():
    """Logout endpoint."""
    response = JSONResponse(content={"success": True})
    response.delete_cookie(key="user_id")
    return response


@router.get("/user", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user info."""
    return UserResponse(
        id=current_user['id'],
        email=current_user['email'],
        created_at=str(current_user.get('created_at', '')),
        role=current_user.get('role', 'user')
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password endpoint."""
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
        
    success = auth_service.reset_password(request.email, request.new_password)
    
    if not success:
        # Don't reveal if user exists or not for security, but for now helpful
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return {"success": True, "message": "Password reset successfully"}
