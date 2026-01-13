"""
Chat routes
Following Single Responsibility Principle - Only handles chat endpoints
Following Dependency Inversion Principle - Depends on service abstractions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from api.dependencies import get_chat_service, get_current_user, get_vanna_instance
from services import ChatService

router = APIRouter()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Create new chat session request."""
    first_message: str


class UpdateTitleRequest(BaseModel):
    """Update session title request."""
    title: str


class SessionResponse(BaseModel):
    """Chat session response."""
    id: str
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Chat message response."""
    id: int
    role: str
    content: str
    sql_query: Optional[str] = None
    data: Optional[List[dict]] = None
    plotly_json: Optional[dict] = None
    created_at: str


@router.post("/chat/new", response_model=dict)
async def create_new_session(
    request_data: CreateSessionRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    vn = Depends(get_vanna_instance)
):
    """
    Yeni sohbet oturumu başlatır.
    İlk mesaj ile otomatik başlık oluşturur.
    """
    user_id = current_user['id']
    first_message = request_data.first_message
    
    # Otomatik başlık oluştur
    title = chat_service.generate_session_title(vn, first_message)
    
    # Session oluştur
    session_id = chat_service.create_session(user_id, title)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )
    
    # İlk mesajı kaydet
    chat_service.add_message(session_id, 'user', first_message)
    
    return {
        "success": True,
        "session_id": session_id,
        "title": title
    }


@router.get("/chat/history", response_model=dict)
async def get_chat_history(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Kullanıcının tüm sohbet geçmişini getirir."""
    user_id = current_user['id']
    sessions = chat_service.get_user_sessions(user_id)
    
    return {
        "success": True,
        "sessions": sessions
    }


@router.get("/chat/{session_id}", response_model=dict)
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Belirli bir sohbetin tüm mesajlarını getirir."""
    user_id = current_user['id']
    
    # Session'ın var olduğunu ve kullanıcıya ait olduğunu kontrol et
    session = chat_service.get_session_by_id(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = chat_service.get_session_messages(session_id, user_id)
    
    return {
        "success": True,
        "session": session,
        "messages": messages
    }


@router.patch("/chat/{session_id}/title", response_model=dict)
async def update_session_title(
    session_id: str,
    request_data: UpdateTitleRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Sohbet başlığını günceller."""
    user_id = current_user['id']
    
    success = chat_service.update_session_title(
        session_id,
        request_data.title,
        user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or update failed"
        )
    
    return {
        "success": True,
        "message": "Title updated successfully"
    }


@router.patch("/chat/{session_id}/pin", response_model=dict)
async def toggle_pin_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Session'ın pin durumunu değiştirir (toggle)."""
    user_id = current_user['id']
    
    success = chat_service.toggle_pin_session(session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or pin toggle failed"
        )
    
    return {
        "success": True,
        "message": "Pin status updated successfully"
    }


@router.delete("/chat/{session_id}", response_model=dict)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Sohbet oturumunu siler."""
    user_id = current_user['id']
    
    success = chat_service.delete_session(session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or delete failed"
        )
    
    return {
        "success": True,
        "message": "Session deleted successfully"
    }
