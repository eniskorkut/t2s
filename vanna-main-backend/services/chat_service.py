"""
Chat Service - Single Responsibility: Chat session and message operations.
SOLID: Single Responsibility Principle
"""
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from src.db import prisma

class ChatService:
    """Service for handling chat session operations using Prisma."""
    
    def __init__(self):
        """Initialize chat service."""
        pass
    
    def generate_session_title(self, vn, first_message: str) -> str:
        """
        LLM kullanarak sohbet için otomatik başlık oluşturur.
        (Synchronous method as it uses Vanna/LLM which might be sync)
        """
        try:
            prompt_text = (
                f"Kullanıcı şu soruyu sordu: '{first_message}'. "
                f"Bu sohbet için 3-5 kelimelik, kısa ve açıklayıcı bir başlık oluştur. "
                f"Sadece başlığı döndür, başka bir şey ekleme. "
                f"Örnek: 'Çalışan Maaş Analizi' veya 'Departman İstatistikleri'"
            )
            
            prompt = [
                vn.system_message("Sen bir başlık oluşturma asistanısın. Kısa, öz ve açıklayıcı başlıklar oluşturursun."),
                vn.user_message(prompt_text)
            ]
            
            title = vn.submit_prompt(prompt)
            
            # Temizle: Tırnak işaretlerini kaldır, max 50 karakter
            if title:
                title = title.strip().strip('"').strip("'").strip()
                if len(title) > 50:
                    title = title[:47] + "..."
                return title
            
            # Fallback
            words = first_message.split()[:4]
            return " ".join(words) + ("..." if len(first_message.split()) > 4 else "")
            
        except Exception as e:
            print(f"Warning: Failed to generate auto title: {e}")
            words = first_message.split()[:4]
            return " ".join(words) + ("..." if len(first_message.split()) > 4 else "")
    
    async def create_session(self, user_id: int, title: str) -> Optional[str]:
        """Yeni bir chat session oluşturur."""
        try:
            session = await prisma.chatsession.create(
                data={
                    'title': title,
                    'user_id': user_id,
                    'is_pinned': False
                }
            )
            return session.id
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    async def update_session_title(self, session_id: str, new_title: str, user_id: int) -> bool:
        """Sohbet başlığını günceller."""
        try:
            session = await prisma.chatsession.update_many(
                where={
                    'id': session_id,
                    'user_id': user_id
                },
                data={
                    'title': new_title
                }
            )
            return session > 0 # count
        except Exception:
            return False
    
    async def get_user_sessions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Kullanıcının tüm sohbetlerini getirir."""
        sessions = await prisma.chatsession.find_many(
            where={'user_id': user_id},
            order=[
                {'is_pinned': 'desc'},
                {'updated_at': 'desc'}
            ],
            take=limit
        )
        
        return [
            {
                'id': s.id,
                'title': s.title,
                'is_pinned': s.is_pinned,
                'created_at': s.created_at.isoformat(),
                'updated_at': s.updated_at.isoformat()
            }
            for s in sessions
        ]
    
    async def get_session_by_id(self, session_id: str, user_id: int) -> Optional[Dict]:
        """Belirli bir session bilgisini getirir."""
        session = await prisma.chatsession.find_first(
            where={
                'id': session_id,
                'user_id': user_id
            }
        )
        
        if session:
            return {
                'id': session.id,
                'title': session.title,
                'is_pinned': session.is_pinned,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }
        return None
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sql_query: Optional[str] = None,
        data: Optional[List[Dict]] = None,
        plotly_json: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Sohbete yeni mesaj ekler."""
        try:
            # JSON serialize
            data_json = json.dumps(data) if data else None
            plotly_json_str = json.dumps(plotly_json) if plotly_json else None
            
            message = await prisma.chatmessage.create(
                data={
                    'session_id': session_id,
                    'role': role,
                    'content': content,
                    'sql_query': sql_query,
                    'data': data_json,
                    'plotly_json': plotly_json_str
                }
            )
            
            # Update session timestamp
            await self._update_session_timestamp(session_id)
            
            return {
                "id": str(message.id),
                "role": role,
                "content": content,
                "sql": sql_query,
                "data": data,
                "plotly_json": plotly_json,
                "created_at": message.created_at.isoformat()
            }
        except Exception as e:
            print(f"Error adding message: {e}")
            return None

    async def get_session_messages(
        self,
        session_id: str,
        user_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """Belirli bir session'ın mesajlarını getirir."""
        # Check ownership first
        session = await self.get_session_by_id(session_id, user_id)
        if not session:
            return []
            
        messages = await prisma.chatmessage.find_many(
            where={'session_id': session_id},
            order={'created_at': 'asc'},
            take=limit
        )
        
        result = []
        for msg in messages:
            msg_data = None
            msg_plotly = None
            
            if msg.data:
                try:
                    msg_data = json.loads(msg.data)
                except: pass
            
            if msg.plotly_json:
                try:
                    msg_plotly = json.loads(msg.plotly_json)
                except: pass
                
            result.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'sql': msg.sql_query,
                'data': msg_data,
                'plotly_json': msg_plotly,
                'created_at': msg.created_at.isoformat()
            })
            
        return result
    
    async def delete_session(self, session_id: str, user_id: int) -> bool:
        """Session siler."""
        try:
            # First check ownership (Prisma deleteMany returns count)
            count = await prisma.chatsession.delete_many(
                where={
                    'id': session_id,
                    'user_id': user_id
                }
            )
            return count > 0
        except Exception:
            return False
            
    async def toggle_pin_session(self, session_id: str, user_id: int) -> bool:
        """Pin durumunu değiştirir."""
        try:
            session = await prisma.chatsession.find_first(
                where={'id': session_id, 'user_id': user_id}
            )
            if not session:
                return False
                
            new_pin = not session.is_pinned
            
            await prisma.chatsession.update(
                where={'id': session_id},
                data={'is_pinned': new_pin}
            )
            return True
        except Exception:
            return False

    async def _update_session_timestamp(self, session_id: str):
        """Update session timestamp."""
        try:
            await prisma.chatsession.update(
                where={'id': session_id},
                data={'updated_at': datetime.now()}
            )
        except: pass

