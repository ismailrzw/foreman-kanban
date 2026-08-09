"""
Task model — the core domain object.
Stages represent the Kanban column: todo → in_progress → submitted_for_review → done
The submitted_for_review → done/rejected transition mirrors a PR review/merge flow.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
    deadline: datetime | None = Field(None, description="Optional deadline — ISO 8601 format")


class TaskUpdate(BaseModel):
    """Schema for updating a task (Manager only)."""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    assigned_to: str | None = None
    complexity: ComplexityType | None = None
    stage: StageType | None = None
    deadline: datetime | None = None



class TaskSubmitForReview(BaseModel):
    """Schema for employee submitting task for review (empty body — action-based)."""


class TaskReviewAction(BaseModel):
    """Schema for manager confirming or rejecting a submission."""
    action: Literal["confirm", "reject"] = Field(..., description="confirm or reject")
    feedback: str | None = Field(
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
    assigned_to_name: str | None = None
    complexity: ComplexityType
    stage: StageType
    is_rejected: bool = False
    rejection_feedback: str | None = None
    revision_history: list[RevisionEntry] = []
    revision_count: int = 0
    deadline: datetime | None = None
    is_overdue: bool = False
    completed_at: datetime | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime