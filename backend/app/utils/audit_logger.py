from datetime import datetime, timezone
from app.core.database import get_database
from app.models.audit import AuditLogEntry

async def log_audit(
    task_id: str,
    action: str,
    user: dict,
    previous_stage: str = None,
    new_stage: str = None,
    details: str = None
):
    """
    Inserts a new AuditLogEntry document into the database audit_logs collection.
    """
    db = get_database()
    entry = AuditLogEntry(
        task_id=task_id,
        action=action,
        performed_by=user["firebase_uid"],
        performed_by_name=user.get("name", "Unknown"),
        performed_by_role=user.get("role", "employee"),
        previous_stage=previous_stage,
        new_stage=new_stage,
        details=details,
        timestamp=datetime.now(timezone.utc)
    )
    await db.audit_logs.insert_one(entry.model_dump())
