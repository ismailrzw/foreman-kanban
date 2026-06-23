"""
Task model — the core domain object.
Stages represent the Kanban column: todo → in_progress → submitted_for_review → done
The submitted_for_review → done/rejected transition mirrors a PR review/merge flow.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


# Valid stage values — these map to Kanban columns
StageType = Literal["todo", "in_progress", "submitted_for_review", "done"]

# Valid complexity levels
ComplexityType = Literal[1, 2, 3]


class TaskCreate(BaseModel):
    """Schema for creating a new task (Manager only)."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=1000, description="Task description")
    assigned_to: str = Field(..., description="Firebase UID of the assigned employee")
    complexity: ComplexityType = Field(default=2, description="1=Low, 2=Medium, 3=High")


class TaskUpdate(BaseModel):
    """Schema for updating a task (Manager only)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assigned_to: Optional[str] = None
    complexity: Optional[ComplexityType] = None
    stage: Optional[StageType] = None


class TaskSubmitForReview(BaseModel):
    """Schema for employee submitting task for review (empty body — action-based)."""
    pass


class TaskReviewAction(BaseModel):
    """Schema for manager confirming or rejecting a submission."""
    action: Literal["confirm", "reject"] = Field(..., description="confirm or reject")
    feedback: Optional[str] = Field(
        None, max_length=500, description="Required when rejecting — reason for rejection"
    )


class RevisionEntry(BaseModel):
    """A single rejection/revision record."""
    revision_number: int
    rejected_at: datetime
    feedback: str
    rejected_by: str  # Firebase UID of the manager who rejected


class TaskResponse(BaseModel):
    """Schema for task data returned by the API."""
    id: str = Field(..., description="MongoDB document _id as string")
    title: str
    description: str
    assigned_to: str
    assigned_to_name: Optional[str] = None
    complexity: ComplexityType
    stage: StageType
    is_rejected: bool = False
    rejection_feedback: Optional[str] = None
    revision_history: list[RevisionEntry] = []
    revision_count: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime