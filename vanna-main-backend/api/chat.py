"""
Chat routes
Following Single Responsibility Principle - Only handles chat endpoints
Following Dependency Inversion Principle - Depends on service abstractions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from api.dependencies import get_chat_service, get_current_user, get_vanna_instance
from models.schemas import ChatMessageRequest
from services import ChatService, QueryService
import json
import asyncio
import hashlib
import time

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
    session_id = await chat_service.create_session(user_id, title)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )
    
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
    sessions = await chat_service.get_user_sessions(user_id)
    
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
    session = await chat_service.get_session_by_id(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = await chat_service.get_session_messages(session_id, user_id)
    
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
    
    success = await chat_service.update_session_title(
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
    
    success = await chat_service.toggle_pin_session(session_id, user_id)
    
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
    
    success = await chat_service.delete_session(session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or delete failed"
        )
    
    return {
        "success": True,
        "message": "Session deleted successfully"
    }


@router.post("/chat/{session_id}/message")
async def send_message(
    session_id: str,
    request_data: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    vn = Depends(get_vanna_instance)
):
    """
    Unified endpoint to handle chat messages.
    Saves user message, generates SQL, executes it, and saves results.
    """
    user_id = current_user['id']
    question = request_data.question
    history = request_data.history
    stream = request_data.stream

    start_time = time.monotonic()
    # Verify session ownership
    print(f"DEBUG: Checking session {session_id} for user {user_id}")
    session = await chat_service.get_session_by_id(session_id, user_id)
    if not session:
        print(f"DEBUG: Session {session_id} not found for user {user_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    print(f"DEBUG: Session found: {session}")

    # 1. Save User Message
    await chat_service.add_message(session_id, 'user', question)

    if stream:
        async def message_generator():
            full_sql = ""
            sql_explanation = ""
            
            # Step 0: Semantic cache check (fast path)
            try:
                cached_sql = QueryService.check_semantic_cache(vn, question)
                if cached_sql:
                    full_sql = cached_sql.strip()
                    sql_explanation = QueryService.generate_sql_explanation(question, full_sql)
                    full_content = f"{sql_explanation}\n\n```sql\n{full_sql}\n```" if sql_explanation else f"```sql\n{full_sql}\n```"
                    await chat_service.add_message(
                        session_id=session_id,
                        role='assistant',
                        content=full_content,
                        sql_query=full_sql
                    )
                    yield f"data: {json.dumps({'type': 'metadata', 'explanation': sql_explanation, 'sql': full_sql, 'from_cache': True})}\n\n"
                    # Run SQL
                    try:
                        df = vn.run_sql(sql=full_sql)
                        data = df.head(10).to_dict(orient="records")
                        plotly_json = None
                        if QueryService.should_generate_chart(df, full_sql):
                            plotly_json = QueryService.generate_plotly_chart(df, full_sql)
                        await chat_service.add_message(
                            session_id=session_id,
                            role='assistant',
                            content="Sorgu sonuçları:",
                            sql_query=full_sql,
                            data=data,
                            plotly_json=plotly_json
                        )
                        yield f"data: {json.dumps({'type': 'result', 'data': data, 'plotly_json': plotly_json, 'from_cache': True})}\n\n"
                    except Exception as e:
                        friendly_error = QueryService.generate_friendly_error(vn, question, full_sql, str(e))
                        await chat_service.add_message(session_id, 'assistant', friendly_error)
                        yield f"data: {json.dumps({'type': 'error', 'error': friendly_error, 'from_cache': True})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
            except Exception as e:
                print(f"Warning: cache lookup failed: {e}")

            # Step 1: Contextualize if history exists
            process_question = question
            if history:
                try:
                    recent_history = history[-5:]
                    history_text = ""
                    for msg in recent_history:
                        history_text += f"{msg.role}: {msg.content}\n"
                    
                    prompt = f"Konuşma Geçmişi:\n{history_text}\n\nKullanıcının Son Sorusu: {question}\n\nGörevin: Kullanıcının son sorusunu, geçmiş konuşma bağlamını kullanarak tek başına anlaşılabilir, bağımsız bir soruya dönüştürmek. Sadece yeniden yazılmış soruyu döndür."
                    system_msg = vn.system_message("Sen bir soru netleştirme asistanısın.")
                    user_msg = vn.user_message(prompt)
                    contextual_question = vn.submit_prompt([system_msg, user_msg])
                    if contextual_question and contextual_question.strip():
                        process_question = contextual_question.strip()
                except: pass

            # Step 2: Generate SQL Stream
            try:
                raw_sql_response = ""
                for token in vn.generate_sql_stream(question=process_question):
                    raw_sql_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0.01)
                
                # Step 3: Extract clean SQL from response (LLM bazen açıklama metni de üretebilir)
                import re
                
                # Önce Vanna'nın extract_sql metodunu dene
                if hasattr(vn, 'extract_sql'):
                    full_sql = vn.extract_sql(raw_sql_response)
                else:
                    # Manuel extraction: markdown code block'lardan SQL çıkar
                    sql_match = re.search(r'```sql\s*\n(.*?)```', raw_sql_response, re.DOTALL | re.IGNORECASE)
                    if sql_match:
                        full_sql = sql_match.group(1).strip()
                    else:
                        # SELECT ile başlayan kısmı bul
                        select_match = re.search(r'\bSELECT\b.*?;', raw_sql_response, re.DOTALL | re.IGNORECASE)
                        if select_match:
                            full_sql = select_match.group(0).strip()
                        else:
                            # Son çare: raw response'u kullan
                            full_sql = raw_sql_response.strip()
                
                # SQL güvenlik kontrolü (sadece validate et, hata fırlatma)
                try:
                    QueryService.validate_sql_safety(full_sql)
                except ValueError as ve:
                    # Güvenlik hatası varsa, SQL'i temizle ve hata mesajı gönder
                    yield f"data: {json.dumps({'type': 'error', 'error': str(ve)})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # Step 4: Finalize SQL
                sql_explanation = QueryService.generate_sql_explanation(process_question, full_sql)
                full_content = f"{sql_explanation}\n\n```sql\n{full_sql}\n```" if sql_explanation else f"```sql\n{full_sql}\n```"
                
                # Save SQL message
                await chat_service.add_message(
                    session_id=session_id,
                    role='assistant',
                    content=full_content,
                    sql_query=full_sql
                )
                
                yield f"data: {json.dumps({'type': 'metadata', 'explanation': sql_explanation, 'sql': full_sql})}\n\n"

                # Step 5: Execute SQL
                try:
                    df = vn.run_sql(sql=full_sql)
                    data = df.head(10).to_dict(orient="records")
                    plotly_json = None
                    if QueryService.should_generate_chart(df, full_sql):
                        plotly_json = QueryService.generate_plotly_chart(df, full_sql)
                    
                    # Save results message
                    await chat_service.add_message(
                        session_id=session_id,
                        role='assistant',
                        content="Sorgu sonuçları:",
                        sql_query=full_sql,
                        data=data,
                        plotly_json=plotly_json
                    )
                    
                    yield f"data: {json.dumps({'type': 'result', 'data': data, 'plotly_json': plotly_json})}\n\n"
                except Exception as e:
                    friendly_error = QueryService.generate_friendly_error(vn, process_question, full_sql, str(e))
                    await chat_service.add_message(session_id, 'assistant', friendly_error)
                    yield f"data: {json.dumps({'type': 'error', 'error': friendly_error})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
                yield "data: [DONE]\n\n"
            finally:
                duration = time.monotonic() - start_time
                print(f"[Perf] send_message stream session={session_id} user={user_id} duration={duration:.2f}s question=\"{question[:80]}\"")

        return StreamingResponse(message_generator(), media_type="text/event-stream")
    else:
        try:
            # Non-streaming implementation (simplified)
            # For now we mostly care about streaming as it's what the UI uses
            full_sql = vn.generate_sql(question=question)
            sql_explanation = QueryService.generate_sql_explanation(question, full_sql)
            full_content = f"{sql_explanation}\n\n```sql\n{full_sql}\n```" if sql_explanation else f"```sql\n{full_sql}\n```"
            await chat_service.add_message(
                session_id=session_id,
                role='assistant',
                content=full_content,
                sql_query=full_sql
            )
            df = vn.run_sql(sql=full_sql)
            data = df.head(10).to_dict(orient="records")
            plotly_json = QueryService.generate_plotly_chart(df, full_sql) if QueryService.should_generate_chart(df, full_sql) else None
            await chat_service.add_message(
                session_id=session_id,
                role='assistant',
                content="Sorgu sonuçları:",
                sql_query=full_sql,
                data=data,
                plotly_json=plotly_json
            )
            return {
                "type": "df",
                "data": data,
                "plotly_json": plotly_json,
                "sql": full_sql
            }
        finally:
            duration = time.monotonic() - start_time
            print(f"[Perf] send_message non-stream session={session_id} user={user_id} duration={duration:.2f}s question=\"{question[:80]}\"")
