from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    """Schema representing a single transition or mutation audit entry for tasks."""

    task_id: str
    action: str  # "created", "started", "submitted", "confirmed", "rejected", "updated", "deleted"
    performed_by: str  # Firebase UID
    performed_by_name: str
    performed_by_role: str
    previous_stage: Optional[str] = None
    new_stage: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime
