"""
Task routes — full CRUD + role-scoped actions.

Manager can:
  - Create tasks (POST /api/tasks)
  - Update tasks (PUT /api/tasks/{id})
  - Delete tasks (DELETE /api/tasks/{id})
  - List all tasks (GET /api/tasks)
  - Review submissions: confirm or reject (POST /api/tasks/{id}/review)

Employee can:
  - List their assigned tasks only (GET /api/tasks)
  - Submit a task for review (POST /api/tasks/{id}/submit)

The core PR-review-merge flow:
  Employee calls POST /api/tasks/{id}/submit → stage becomes 'submitted_for_review'
  Manager calls POST /api/tasks/{id}/review with action=confirm → stage becomes 'done'
  Manager calls POST /api/tasks/{id}/review with action=reject → stage becomes 'in_progress'
"""

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone
from app.middleware.role_guard import require_role
from app.models.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskReviewAction,
    RevisionEntry,
)
from app.utils.status_machine import validate_transition
from app.core.database import get_database

router = APIRouter(prefix="/api", tags=["tasks"])


def task_doc_to_response(doc: dict, users_cache: dict = None) -> TaskResponse:
    """Convert a MongoDB task document to a TaskResponse schema."""
    assigned_to_name = None
    if users_cache and doc.get("assigned_to") in users_cache:
        assigned_to_name = users_cache[doc["assigned_to"]]

    deadline = doc.get("deadline")
    is_overdue = False
    if deadline and doc.get("stage") != "done":
        now = datetime.now(timezone.utc) if deadline.tzinfo else datetime.now()
        is_overdue = deadline < now

    return TaskResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description", ""),
        assigned_to=doc["assigned_to"],
        assigned_to_name=assigned_to_name,
        complexity=doc["complexity"],
        stage=doc["stage"],
        is_rejected=doc.get("is_rejected", False),
        rejection_feedback=doc.get("rejection_feedback"),
        revision_history=doc.get("revision_history", []),
        revision_count=doc.get("revision_count", 0),
        deadline=deadline,
        is_overdue=is_overdue,
        completed_at=doc.get("completed_at"),
        created_by=doc["created_by"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )




# ─── LIST TASKS ──────────────────────────────────────────────

@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    current_user: dict = Depends(require_role()),  # Any authenticated user
):
    """
    List tasks — scoped by role:
    - Manager: sees ALL tasks
    - Employee: sees only tasks assigned to them
    """
    db = get_database()

    # Build query based on role
    if current_user["role"] == "manager":
        query = {}
    else:
        query = {"assigned_to": current_user["firebase_uid"]}

    # Build a user name cache for assigned_to_name
    users_cache = {}
    async for user in db.users.find({"role": "employee"}):
        users_cache[user["firebase_uid"]] = user["name"]

    # Fetch tasks sorted by creation date (newest first)
    cursor = db.tasks.find(query).sort("created_at", -1)
    tasks = []
    async for doc in cursor:
        tasks.append(task_doc_to_response(doc, users_cache))
    return tasks


# ─── CREATE TASK (Manager only) ─────────────────────────────

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(require_role("manager")),
):
    """
    Create a new task (Manager only).
    Initial stage is always 'todo'.
    """
    db = get_database()

    # Verify the assigned employee exists
    employee = await db.users.find_one({
        "firebase_uid": task_data.assigned_to,
        "role": "employee",
    })
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user not found or is not an employee.",
        )

    now = datetime.now(timezone.utc)
    doc = {
        "title": task_data.title,
        "description": task_data.description,
        "assigned_to": task_data.assigned_to,
        "complexity": task_data.complexity,
        "stage": "todo",
        "is_rejected": False,
        "rejection_feedback": None,
        "revision_history": [],
        "revision_count": 0,
        "deadline": task_data.deadline,
        "completed_at": None,
        "created_by": current_user["firebase_uid"],
        "created_at": now,
        "updated_at": now,
    }


    result = await db.tasks.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Get assignee name for response
    users_cache = {employee["firebase_uid"]: employee["name"]}
    return task_doc_to_response(doc, users_cache)


# ─── UPDATE TASK (Manager only) ─────────────────────────────

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(require_role("manager")),
):
    """
    Update a task's metadata (Manager only).
    For stage transitions, use the dedicated /submit and /review endpoints.
    """
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Build update dict (only explicitly set fields)
    update_fields = task_data.model_dump(exclude_unset=True)


    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update.")

    # If stage is being changed, validate the transition
    if "stage" in update_fields:
        is_valid, error = validate_transition(
            task["stage"], update_fields["stage"], current_user["role"]
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_fields},
    )

    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return task_doc_to_response(updated)


# ─── DELETE TASK (Manager only) ──────────────────────────────

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(require_role("manager")),
):
    """Delete a task (Manager only)."""
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found.")


# ─── SUBMIT FOR REVIEW (Employee only) ──────────────────────

@router.post("/tasks/{task_id}/submit", response_model=TaskResponse)
async def submit_for_review(
    task_id: str,
    current_user: dict = Depends(require_role("employee")),
):
    """
    Employee submits a task for manager review.
    This is the equivalent of "opening a Pull Request."

    - Task must be in 'in_progress' stage
    - Only the assigned employee can submit
    - Transitions stage to 'submitted_for_review'
    """
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Only the assigned employee can submit
    if task["assigned_to"] != current_user["firebase_uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit tasks assigned to you.",
        )

    # Validate transition using the status machine
    is_valid, error = validate_transition(
        task["stage"], "submitted_for_review", current_user["role"]
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Perform the transition
    now = datetime.now(timezone.utc)
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {
            "stage": "submitted_for_review",
            "is_rejected": False,
            "rejection_feedback": None,
            "updated_at": now,
        }},
    )

    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return task_doc_to_response(updated)


# ─── START TASK (Employee only) ──────────────────────────────

@router.post("/tasks/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: str,
    current_user: dict = Depends(require_role("employee")),
):
    """
    Employee starts working on a task.
    Transitions stage from 'todo' to 'in_progress'.
    """
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Only the assigned employee can start
    if task["assigned_to"] != current_user["firebase_uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only start tasks assigned to you.",
        )

    # Validate transition
    is_valid, error = validate_transition(
        task["stage"], "in_progress", current_user["role"]
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    now = datetime.now(timezone.utc)
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"stage": "in_progress", "updated_at": now}},
    )

    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return task_doc_to_response(updated)


# ─── REVIEW TASK (Manager only) ─────────────────────────────

@router.post("/tasks/{task_id}/review", response_model=TaskResponse)
async def review_task(
    task_id: str,
    review_data: TaskReviewAction,
    current_user: dict = Depends(require_role("manager")),
):
    """
    Manager reviews a submitted task — confirms (merge) or rejects (request changes).
    This is the PR review/merge analog.

    - Task must be in 'submitted_for_review' stage
    - action='confirm' → moves to 'done' (merged)
    - action='reject' → moves back to 'in_progress' (changes requested) with feedback
    """
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if task["stage"] != "submitted_for_review":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review a task in '{task['stage']}' stage. "
                   f"Task must be in 'submitted_for_review' stage.",
        )

    now = datetime.now(timezone.utc)

    if review_data.action == "confirm":
        # Validate transition
        is_valid, error = validate_transition(
            task["stage"], "done", current_user["role"]
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "stage": "done",
                "is_rejected": False,
                "rejection_feedback": None,
                "completed_at": now,
                "updated_at": now,
            }},
        )


    elif review_data.action == "reject":
        if not review_data.feedback:
            raise HTTPException(
                status_code=400,
                detail="Feedback is required when rejecting a task.",
            )

        # Validate transition
        is_valid, error = validate_transition(
            task["stage"], "in_progress", current_user["role"]
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        new_revision_number = task.get("revision_count", 0) + 1
        revision_entry = {
            "revision_number": new_revision_number,
            "rejected_at": now,
            "feedback": review_data.feedback,
            "rejected_by": current_user["firebase_uid"],
        }

        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "stage": "in_progress",
                    "is_rejected": True,
                    "rejection_feedback": review_data.feedback,
                    "updated_at": now,
                },
                "$push": {
                    "revision_history": revision_entry
                },
                "$inc": {
                    "revision_count": 1
                }
            },
        )

    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return task_doc_to_response(updated)


# ─── OVERDUE TASKS (Manager only) ─────────────────────────────

@router.get("/tasks/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Get all overdue tasks (Manager only).
    """
    db = get_database()
    now = datetime.now(timezone.utc)

    # Query non-done tasks with deadlines in the past
    query = {
        "stage": {"$ne": "done"},
        "deadline": {"$ne": None, "$lt": now}
    }

    # Build a user name cache for assigned_to_name
    users_cache = {}
    async for user in db.users.find({"role": "employee"}):
        users_cache[user["firebase_uid"]] = user["name"]

    cursor = db.tasks.find(query).sort("deadline", 1)
    tasks = []
    async for doc in cursor:
        tasks.append(task_doc_to_response(doc, users_cache))
    return tasks


# ─── TASK HISTORY (Manager only) ──────────────────────────────

@router.get("/tasks/{task_id}/history")
async def get_task_history(
    task_id: str,
    current_user: dict = Depends(require_role("manager")),
):
    """
    Get the revision history for a task (Manager only).
    """
    db = get_database()

    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task_id,
        "revision_count": task.get("revision_count", 0),
        "revisions": task.get("revision_history", []),
    }