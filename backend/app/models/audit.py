from datetime import datetime

from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    """Schema representing a single transition or mutation audit entry for tasks."""

    task_id: str
    action: str  # "created", "started", "submitted", "confirmed", "rejected", "updated", "deleted"
    performed_by: str  # Firebase UID
    performed_by_name: str
    performed_by_role: str
    previous_stage: str | None = None
    new_stage: str | None = None
    details: str | None = None
    timestamp: datetime
