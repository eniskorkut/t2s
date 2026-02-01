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
from services import UserService, DatabaseService, QueryService, ScannerService
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
    users = await user_service.get_all_users()
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

    success = await user_service.update_user_role(user_id, request.role)
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


from src.db import prisma

@router.get("/ddl/saved", response_model=SchemaDefinition, dependencies=[Depends(require_admin)])
async def get_saved_ddl(
    user_service: UserService = Depends(get_user_service)
):
    """Get the last saved DDL definition."""
    result = await prisma.schemadefinition.find_first(
        order={'created_at': 'desc'}
    )
    
    if not result:
        return {
            "id": 0,
            "user_id": 0,
            "ddl_content": "",
            "created_at": ""
        }
        
    return {
        "id": result.id,
        "user_id": result.user_id,
        "ddl_content": result.ddl_content,
        "created_at": result.created_at.isoformat()
    }


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
    
    # 1. Save DDL to DB (Prisma)
    try:
        await prisma.schemadefinition.create(
            data={
                'user_id': current_user['id'],
                'ddl_content': request.ddl
            }
        )
    except Exception as e:
        print(f"Error saving DDL: {e}")
        # Proceed with training anyway
        pass
    
    # 2. Train Vanna in Background
    # Training and cache clearing can take time, so we offload it
    background_tasks.add_task(run_training_job, vn, request.ddl)
    
    return {"success": True, "message": "Training started in background"}


@router.post("/scan-data", dependencies=[Depends(require_admin)])
async def scan_data(
    background_tasks: BackgroundTasks,
    vn = Depends(get_vanna_instance),
    current_user: dict = Depends(require_admin)
):
    """
    Trigger manual data scan to index categorical values.
    """
    background_tasks.add_task(ScannerService.scan_and_train, vn)
    background_tasks.add_task(ScannerService.scan_and_train, vn)
    return {"success": True, "message": "Data scan started in background"}


@router.get("/scanner-status", dependencies=[Depends(require_admin)])
async def get_scanner_status():
    """Get status of the data scanner."""
    return ScannerService.get_status()


def run_training_job(vn, ddl_content: str):
    """Background task to run Vanna training."""
    try:
        print("🚀 Starting background training job...")
        vn.train(ddl=ddl_content)
        print("✅ Training completed.")
        
        # 3. Clear Cache
        QueryService.clear_cache(vn)
        print("🧹 Cache cleared.")
    except Exception as e:
        print(f"❌ Training failed: {e}")
