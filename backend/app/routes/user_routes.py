"""
User routes — manager-only endpoints for user management.
Primary use: populating the "Assign to" dropdown when creating tasks.
"""

from fastapi import APIRouter, Depends
from app.middleware.role_guard import require_role
from app.models.user import UserResponse
from app.core.database import get_database

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users/employees", response_model=list[UserResponse])
async def list_employees(
    current_user: dict = Depends(require_role("manager")),
):
    """
    List all employees (Manager only).
    Used to populate the assignment dropdown in the "New Work Order" modal.
    """
    db = get_database()
    cursor = db.users.find({"role": "employee"})
    employees = []
    async for user in cursor:
        employees.append(UserResponse(**user))
    return employees