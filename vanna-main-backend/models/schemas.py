"""
Pydantic models for request/response validation
Following Single Responsibility Principle - Data validation only
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Register request model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    created_at: Optional[str] = None
    role: str = "user"

    class Config:
        from_attributes = True


class UpdateUserRoleRequest(BaseModel):
    """Update user role request model."""
    role: str


class DDLResponse(BaseModel):
    """DDL response model."""
    ddl: str


class DDLTrainRequest(BaseModel):
    """DDL training request model."""
    ddl: str


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    email: str
    new_password: str


class SchemaDefinition(BaseModel):
    """Schema definition model."""
    id: int
    user_id: int
    ddl_content: str
    created_at: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    user: Optional[UserResponse] = None
    error: Optional[str] = None


class SaveQueryRequest(BaseModel):
    """Save query request model."""
    question: str
    sql_query: str
    is_trained: bool = False


class QueryResponse(BaseModel):
    """Query response model."""
    id: int
    question: str
    sql_query: str
    saved_at: str
    is_trained: bool

    class Config:
        from_attributes = True


class QueriesResponse(BaseModel):
    """Queries list response model."""
    success: bool
    queries: List[QueryResponse]
    error: Optional[str] = None


class RunSqlRequest(BaseModel):
    """Run SQL request model."""
    sql: str
    question: Optional[str] = None  # Kullanıcının sorusu - hata açıklaması için gerekli
    session_id: Optional[str] = None # Mesajı kaydetmek için gerekli


class ChatMessage(BaseModel):
    """Chat message model for history."""
    role: str
    content: str


class GenerateSqlRequest(BaseModel):
    """Generate SQL request model."""
    question: str
    history: List[ChatMessage] = []
    session_id: Optional[str] = None # Mesajı kaydetmek için gerekli


class ChatMessageRequest(BaseModel):
    """Unified chat message request."""
    question: str
    history: List[ChatMessage] = []
    stream: bool = True
