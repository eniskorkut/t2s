"""
Query management routes
Following Single Responsibility Principle - Only handles query endpoints
Following Dependency Inversion Principle - Depends on service abstractions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List
from models.schemas import SaveQueryRequest, QueryResponse, QueriesResponse, RunSqlRequest
from api.dependencies import get_query_service, get_current_user, get_vanna_instance, get_chat_service
from services import QueryService, ChatService

router = APIRouter()


@router.post("/save-query", status_code=status.HTTP_201_CREATED)
async def save_query(
    query_data: SaveQueryRequest,
    current_user: dict = Depends(get_current_user),
    query_service: QueryService = Depends(get_query_service),
    vn = Depends(get_vanna_instance)
):
    """Save a query."""
    user_id = current_user['id']
    query_id = query_service.save_query(
        user_id,
        query_data.question,
        query_data.sql_query,
        query_data.is_trained
    )
    
    if not query_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save query"
        )
    
    # Always train Vanna with the saved query to feed semantic cache
    try:
        vn.train(question=query_data.question, sql=query_data.sql_query)
        print(f"✅ [Training] Successfully trained Vanna with query: \"{query_data.question[:50]}...\"")
    except Exception as e:
        print(f"⚠️  [Training] Failed to train Vanna: {e}")
    
    return {"success": True, "query_id": query_id}


@router.get("/my-queries", response_model=QueriesResponse)
async def get_my_queries(
    current_user: dict = Depends(get_current_user),
    query_service: QueryService = Depends(get_query_service)
):
    """Get user's saved queries."""
    user_id = current_user['id']
    queries = query_service.get_user_queries(user_id)
    
    # Convert to response models
    query_responses = [
        QueryResponse(
            id=q['id'],
            question=q['question'],
            sql_query=q['sql_query'],
            saved_at=str(q['saved_at']),
            is_trained=bool(q.get('is_trained', False))
        )
        for q in queries
    ]
    
    return QueriesResponse(success=True, queries=query_responses)


@router.delete("/query/{query_id}")
async def delete_query(
    query_id: int,
    current_user: dict = Depends(get_current_user),
    query_service: QueryService = Depends(get_query_service)
):
    """Delete a query."""
    user_id = current_user['id']
    success = query_service.delete_query(query_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found or access denied"
        )
    
    return {"success": True}


@router.post("/v0/run_sql")
async def run_sql(
    sql_request: RunSqlRequest,
    request: Request,
    vn = Depends(get_vanna_instance),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Run SQL query and return results.
    POST endpoint that accepts SQL string in request body.
    AI tabanlı hata açıklama özelliği ile hataları kullanıcı dostu mesajlara dönüştürür.
    """
    sql = sql_request.sql.strip()
    question = sql_request.question
    session_id = sql_request.session_id
    
    try:
        # Check if run_sql is set
        if not hasattr(vn, 'run_sql') or not callable(vn.run_sql):
            return JSONResponse(
                status_code=200,
                content={
                    "type": "sql_error",
                    "data": [],
                    "plotly_json": None,
                    "error": "Veritabanı bağlantısı yok.",
                    "sql": sql
                }
            )
        
        # Validate SQL safety
        try:
            QueryService.validate_sql_safety(sql)
        except ValueError as ve:
            return JSONResponse(
                status_code=200,
                content={
                    "type": "sql_error",
                    "data": [],
                    "plotly_json": None,
                    "error": str(ve),
                    "sql": sql
                }
            )

        # Run SQL
        df = vn.run_sql(sql=sql)
        
        # Convert to JSON for response
        data = df.head(10).to_dict(orient="records")
        
        # Generate chart if appropriate
        plotly_json = None
        if QueryService.should_generate_chart(df, sql):
            plotly_json = QueryService.generate_plotly_chart(df, sql)
        
        # Return results (limit to 10 rows for response)
        response_data = {
            "type": "df",
            "data": data,
            "plotly_json": plotly_json,
            "df": df.head(10).to_json(orient="records", date_format="iso"),
            "should_generate_chart": plotly_json is not None,
            "error": None,
            "sql": sql
        }

        # Save results to chat history if session exists
        if session_id:
            try:
                chat_service.add_message(
                    session_id=session_id,
                    role='assistant',
                    content="Sorgu sonuçları:",
                    sql_query=sql,
                    data=data,
                    plotly_json=plotly_json
                )
            except Exception as e:
                print(f"Warning: Failed to save run_sql results to history: {e}")

        return response_data
    except Exception as e:
        error_msg = str(e)
        
        # AI tabanlı dostane hata mesajı oluştur
        friendly_message = QueryService.generate_friendly_error(
            vn=vn,
            question=question,
            sql=sql,
            error_msg=error_msg
        )
        
        # Hata durumunda HTTP 200 döndür (hatayı biz yönettik)
        return JSONResponse(
            status_code=200,
            content={
                "type": "sql_error",
                "data": [],
                "plotly_json": None,
                "error": friendly_message,
                "sql": sql
            }
        )
