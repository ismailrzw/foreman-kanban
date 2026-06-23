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


@router.get("/metrics")
async def get_completion_metrics(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Returns completion metrics (overall and per-employee).
    Handles division-by-zero edge cases.
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

    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t["stage"] == "done"]
    completed_count = len(completed_tasks)
    completion_rate = completed_count / total_tasks if total_tasks > 0 else 0.0

    # Calculate average completion time in hours
    completion_times = []
    for t in completed_tasks:
        created_at = t.get("created_at")
        completed_at = t.get("completed_at")
        if created_at and completed_at:
            delta = completed_at - created_at
            hours = delta.total_seconds() / 3600.0
            completion_times.append(hours)
    avg_completion_time_hours = sum(completion_times) / len(completion_times) if completion_times else 0.0

    # Rejection rate: count of tasks with at least one rejection / total_tasks
    rejected_tasks_count = len([t for t in tasks if t.get("revision_count", 0) > 0])
    overall_rejection_rate = rejected_tasks_count / total_tasks if total_tasks > 0 else 0.0

    overall = {
        "total_tasks": total_tasks,
        "completed": completed_count,
        "completion_rate": completion_rate,
        "avg_completion_time_hours": avg_completion_time_hours,
        "rejection_rate": overall_rejection_rate
    }

    per_employee = []
    for emp in employees:
        emp_uid = emp["firebase_uid"]
        emp_tasks = [t for t in tasks if t["assigned_to"] == emp_uid]
        emp_total = len(emp_tasks)
        emp_completed = [t for t in emp_tasks if t["stage"] == "done"]
        emp_completed_count = len(emp_completed)

        emp_completion_rate = emp_completed_count / emp_total if emp_total > 0 else 0.0

        emp_completion_times = []
        for t in emp_completed:
            created_at = t.get("created_at")
            completed_at = t.get("completed_at")
            if created_at and completed_at:
                delta = completed_at - created_at
                hours = delta.total_seconds() / 3600.0
                emp_completion_times.append(hours)
        emp_avg_completion_time_hours = sum(emp_completion_times) / len(emp_completion_times) if emp_completion_times else 0.0

        emp_rejected_count = len([t for t in emp_tasks if t.get("revision_count", 0) > 0])
        emp_rejection_rate = emp_rejected_count / emp_total if emp_total > 0 else 0.0

        # Complexity distribution
        comp_dist = {"1": 0, "2": 0, "3": 0}
        for t in emp_tasks:
            comp_key = str(t.get("complexity", 2))
            if comp_key in comp_dist:
                comp_dist[comp_key] += 1

        per_employee.append({
            "name": emp["name"],
            "total": emp_total,
            "completed": emp_completed_count,
            "completion_rate": emp_completion_rate,
            "avg_completion_time_hours": emp_avg_completion_time_hours,
            "rejection_rate": emp_rejection_rate,
            "complexity_distribution": comp_dist
        })

    return {
        "overall": overall,
        "per_employee": per_employee
    }

