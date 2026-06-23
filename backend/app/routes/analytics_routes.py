from fastapi import APIRouter, Depends
from app.middleware.role_guard import require_role
from app.core.database import get_database

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/workload")
async def get_workload_dashboard(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Returns workload data for each employee:
    - Number of tasks assigned
    - Sum of complexity values (weighted load)
    - Stage breakdown (count & weight)
    Includes employees with zero tasks.
    """
    db = get_database()

    # 1. Fetch all employees
    employees = []
    async for user in db.users.find({"role": "employee"}):
        employees.append(user)

    # 2. Fetch all tasks
    tasks = []
    async for task in db.tasks.find({}):
        tasks.append(task)

    results = []
    for emp in employees:
        emp_uid = emp["firebase_uid"]
        emp_tasks = [t for t in tasks if t["assigned_to"] == emp_uid]

        total_tasks = len(emp_tasks)
        weighted_load = sum(t["complexity"] for t in emp_tasks)

        by_stage = {}
        for stage in ["todo", "in_progress", "submitted_for_review", "done"]:
            stage_tasks = [t for t in emp_tasks if t["stage"] == stage]
            by_stage[stage] = {
                "count": len(stage_tasks),
                "weight": sum(t["complexity"] for t in stage_tasks)
            }

        results.append({
            "firebase_uid": emp_uid,
            "name": emp["name"],
            "total_tasks": total_tasks,
            "weighted_load": weighted_load,
            "by_stage": by_stage
        })

    return {"employees": results}
