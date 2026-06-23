from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.middleware.role_guard import require_role
from app.core.database import get_database
from app.models.audit import AuditLogEntry

router = APIRouter(prefix="/api", tags=["audit"])

@router.get("/tasks/{task_id}/audit", response_model=list[AuditLogEntry])
async def get_task_audit(
    task_id: str,
    current_user: dict = Depends(require_role("manager")),
):
    """
    Get the full chronological audit trail for a single task (Manager only).
    """
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    cursor = db.audit_logs.find({"task_id": task_id}).sort("timestamp", 1)
    logs = []
    async for doc in cursor:
        logs.append(AuditLogEntry(**doc))
    return logs

@router.get("/audit/recent", response_model=list[AuditLogEntry])
async def get_recent_audit(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Get the last 50 audit logs across all tasks (Manager only).
    """
    db = get_database()
    cursor = db.audit_logs.find({}).sort("timestamp", -1).limit(50)
    logs = []
    async for doc in cursor:
        logs.append(AuditLogEntry(**doc))
    return logs
