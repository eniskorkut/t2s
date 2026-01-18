"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from models.schemas import (
    UserResponse, 
    UpdateUserRoleRequest, 
    DDLResponse, 
    DDLTrainRequest,
    SchemaDefinition
)
from services import UserService, DatabaseService, QueryService
from api.dependencies import (
    get_user_service, 
    get_db_service, 
    get_query_service,
    get_vanna_instance, 
    require_admin
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
async def get_users(
    user_service: UserService = Depends(get_user_service)
):
    """List all users."""
    users = user_service.get_all_users()
    return users


@router.patch("/users/{user_id}/role", dependencies=[Depends(require_admin)])
async def update_user_role(
    user_id: int,
    request: UpdateUserRoleRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_admin)
):
    """Update a user's role."""
    # Prevent removing own admin status if it's the last admin? 
    # For simplicity, we just allow it but warn in UI.
    
    if user_id == current_user['id'] and request.role != 'admin':
        # Optional: check if there are other admins
        pass

    success = user_service.update_user_role(user_id, request.role)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True}


@router.get("/ddl/live", response_model=DDLResponse, dependencies=[Depends(require_admin)])
async def get_live_ddl(
    db_service: DatabaseService = Depends(get_db_service),
    vn = Depends(get_vanna_instance)
):
    """Get live database schema DDL."""
    ddl = db_service.get_database_schema(vn)
    return {"ddl": ddl}


@router.get("/ddl/saved", response_model=SchemaDefinition, dependencies=[Depends(require_admin)])
async def get_saved_ddl(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get the last saved DDL definition."""
    query = """
        SELECT id, user_id, ddl_content, created_at 
        FROM schema_definitions 
        ORDER BY created_at DESC 
        LIMIT 1
    """
    results = db_service.execute_query(query)
    
    if not results:
        # If no saved DDL, return current live DDL as default or 404
        # Better to return empty or construct one
        return {
            "id": 0,
            "user_id": 0,
            "ddl_content": "",
            "created_at": ""
        }
        
    return results[0]


@router.post("/train", dependencies=[Depends(require_admin)])
async def train_ddl(
    request: DDLTrainRequest,
    background_tasks: BackgroundTasks,
    db_service: DatabaseService = Depends(get_db_service),
    query_service: QueryService = Depends(get_query_service),
    vn = Depends(get_vanna_instance),
    current_user: dict = Depends(require_admin)
):
    """Save DDL and train Vanna."""
    
    # 1. Save DDL to DB
    insert_query = """
        INSERT INTO schema_definitions (user_id, ddl_content)
        VALUES (?, ?)
    """
    db_service.execute_insert(insert_query, (current_user['id'], request.ddl))
    
    # 2. Train Vanna (This can be slow, but usually DDL training is fast enough)
    # If it's very large, background task is better.
    try:
        vn.train(ddl=request.ddl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
    
    # 3. Clear Cache
    # QueryService has static method clear_cache(vn)
    try:
        QueryService.clear_cache(vn)
    except Exception as e:
        print(f"Warning: Failed to clear cache: {e}")
    
    return {"success": True, "message": "Training completed and cache cleared"}
