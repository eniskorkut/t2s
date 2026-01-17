"""
Chat Service - Single Responsibility: Chat session and message operations.
SOLID: Single Responsibility Principle
"""
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
from .database_service import DatabaseService


class ChatService:
    """Service for handling chat session operations."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize chat service.
        
        Args:
            db_service: DatabaseService instance
        """
        self.db_service = db_service
    
    def generate_session_title(self, vn, first_message: str) -> str:
        """
        LLM kullanarak sohbet için otomatik başlık oluşturur.
        
        Args:
            vn: Vanna instance (LLM için)
            first_message: Kullanıcının ilk sorusu
            
        Returns:
            Oluşturulan başlık (3-5 kelime)
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
            
            # Fallback: İlk birkaç kelime
            words = first_message.split()[:4]
            return " ".join(words) + ("..." if len(first_message.split()) > 4 else "")
            
        except Exception as e:
            print(f"Warning: Failed to generate auto title: {e}")
            # Fallback başlık
            words = first_message.split()[:4]
            return " ".join(words) + ("..." if len(first_message.split()) > 4 else "")
    
    def create_session(self, user_id: int, title: str) -> Optional[str]:
        """
        Yeni bir chat session oluşturur.
        
        Args:
            user_id: Kullanıcı ID
            title: Sohbet başlığı
            
        Returns:
            Session ID (UUID) veya None
        """
        try:
            session_id = str(uuid.uuid4())
            print(f"DEBUG: Creating session {session_id} for user {user_id}")
            query = """
                INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """
            self.db_service.execute_update(query, (session_id, user_id, title))
            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    def update_session_title(self, session_id: str, new_title: str, user_id: int) -> bool:
        """
        Sohbet başlığını günceller (güvenlik için user_id kontrolü).
        
        Args:
            session_id: Session ID
            new_title: Yeni başlık
            user_id: Kullanıcı ID (güvenlik)
            
        Returns:
            True başarılı, False başarısız
        """
        try:
            query = """
                UPDATE chat_sessions 
                SET title = ?, updated_at = datetime('now')
                WHERE id = ? AND user_id = ?
            """
            rows = self.db_service.execute_update(query, (new_title, session_id, user_id))
            return rows > 0
        except Exception:
            return False
    
    def get_user_sessions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Kullanıcının tüm sohbetlerini getirir (tarihe göre sıralı).
        
        Args:
            user_id: Kullanıcı ID
            limit: Maksimum kayıt sayısı
            
        Returns:
            Session listesi
        """
        query = """
            SELECT id, title, is_pinned, created_at, updated_at
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY is_pinned DESC, updated_at DESC
            LIMIT ?
        """
        results = self.db_service.execute_query(query, (user_id, limit))
        return results
    
    def get_session_by_id(self, session_id: str, user_id: int) -> Optional[Dict]:
        """
        Belirli bir session bilgisini getirir (güvenlik kontrolü ile).
        
        Args:
            session_id: Session ID
            user_id: Kullanıcı ID
            
        Returns:
            Session dict veya None
        """
        query = """
            SELECT id, title, is_pinned, created_at, updated_at
            FROM chat_sessions
            WHERE id = ? AND user_id = ?
        """
        results = self.db_service.execute_query(query, (session_id, user_id))
        return results[0] if results else None
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sql_query: Optional[str] = None,
        data: Optional[List[Dict]] = None,
        plotly_json: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Sohbete yeni mesaj ekler.
        
        Args:
            session_id: Session ID
            role: 'user' veya 'assistant'
            content: Mesaj içeriği
            sql_query: SQL sorgusu (varsa)
            data: Tablo verisi (varsa)
            plotly_json: Grafik verisi (varsa)
            
        Returns:
            Eklenen mesaj (dict) veya None
        """
        try:
            # Ensure session_id is a string
            session_id = str(session_id)
            
            # JSON serialize et
            data_json = json.dumps(data) if data else None
            plotly_json_str = json.dumps(plotly_json) if plotly_json else None
            
            query = """
                INSERT INTO chat_messages 
                (session_id, role, content, sql_query, data, plotly_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            message_id = self.db_service.execute_insert(
                query,
                (session_id, role, content, sql_query, data_json, plotly_json_str)
            )
            
            if not message_id:
                print(f"Warning: execute_insert returned None for session {session_id}")
                return None
            
            # Session'ın updated_at'ini güncelle
            self._update_session_timestamp(session_id)
            
            # Eklenen mesajı geri döndür (frontend için)
            return {
                "id": str(message_id),
                "role": role,
                "content": content,
                "sql": sql_query,
                "data": data,
                "plotly_json": plotly_json,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error adding message to session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_session_messages(
        self,
        session_id: str,
        user_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """
        Belirli bir session'ın tüm mesajlarını getirir.
        
        Args:
            session_id: Session ID
            user_id: Kullanıcı ID (güvenlik)
            limit: Maksimum mesaj sayısı
            
        Returns:
            Mesaj listesi
        """
        # Önce session'ın kullanıcıya ait olduğunu kontrol et
        session = self.get_session_by_id(session_id, user_id)
        if not session:
            return []
        
        query = """
            SELECT id, role, content, sql_query as sql, data, plotly_json, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
        """
        
        results = self.db_service.execute_query(query, (session_id, limit))
        
        # JSON parse et
        for msg in results:
            if msg.get('data'):
                try:
                    msg['data'] = json.loads(msg['data'])
                except:
                    msg['data'] = None
            
            if msg.get('plotly_json'):
                try:
                    msg['plotly_json'] = json.loads(msg['plotly_json'])
                except:
                    msg['plotly_json'] = None
        
        return results
    
    def delete_session(self, session_id: str, user_id: int) -> bool:
        """
        Session'ı siler (cascade delete ile mesajlar da silinir).
        
        Args:
            session_id: Session ID
            user_id: Kullanıcı ID (güvenlik)
            
        Returns:
            True başarılı, False başarısız
        """
        try:
            query = "DELETE FROM chat_sessions WHERE id = ? AND user_id = ?"
            rows = self.db_service.execute_update(query, (session_id, user_id))
            return rows > 0
        except Exception:
            return False
    
    def toggle_pin_session(self, session_id: str, user_id: int) -> bool:
        """
        Session'ın pin durumunu değiştirir (toggle).
        
        Args:
            session_id: Session ID
            user_id: Kullanıcı ID (güvenlik)
            
        Returns:
            True başarılı, False başarısız
        """
        try:
            # Önce mevcut pin durumunu al
            check_query = "SELECT is_pinned FROM chat_sessions WHERE id = ? AND user_id = ?"
            result = self.db_service.execute_query(check_query, (session_id, user_id))
            
            if not result:
                return False
            
            current_pin = result[0].get('is_pinned', 0)
            new_pin = 1 if current_pin == 0 else 0
            
            # Pin durumunu güncelle
            query = """
                UPDATE chat_sessions 
                SET is_pinned = ?, updated_at = datetime('now')
                WHERE id = ? AND user_id = ?
            """
            rows = self.db_service.execute_update(query, (new_pin, session_id, user_id))
            return rows > 0
        except Exception:
            return False
    
    def _update_session_timestamp(self, session_id: str):
        """Session'ın updated_at timestamp'ini günceller (private helper)."""
        try:
            query = "UPDATE chat_sessions SET updated_at = datetime('now') WHERE id = ?"
            self.db_service.execute_update(query, (session_id,))
        except:
            pass
