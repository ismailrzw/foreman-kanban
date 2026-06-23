import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone

def test_rejection_history_flow(client, setup_mocks):
    db = setup_mocks
    
    # 1. Create a task (as Manager)
    create_payload = {
        "title": "Build CI Pipeline",
        "description": "Configure GitHub Actions",
        "assigned_to": "uid-emp",
        "complexity": 2
    }
    headers_mgr = {"Authorization": "Bearer manager-token"}
    response = client.post("/api/tasks", json=create_payload, headers=headers_mgr)
    assert response.status_code == status.HTTP_201_CREATED
    task = response.json()
    task_id = task["id"]
    
    assert task["revision_count"] == 0
    assert task["revision_history"] == []
    
    # 2. Start the task (as Employee)
    headers_emp = {"Authorization": "Bearer employee-token"}
    response = client.post(f"/api/tasks/{task_id}/start", headers=headers_emp)
    assert response.status_code == status.HTTP_200_OK
    
    # 3. Submit the task (as Employee)
    response = client.post(f"/api/tasks/{task_id}/submit", headers=headers_emp)
    assert response.status_code == status.HTTP_200_OK
    
    # 4. Reject the task without feedback (should fail)
    reject_payload_no_feedback = {
        "action": "reject"
    }
    response = client.post(f"/api/tasks/{task_id}/review", json=reject_payload_no_feedback, headers=headers_mgr)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # 5. Reject the task with feedback (as Manager)
    reject_payload = {
        "action": "reject",
        "feedback": "Missing test coverage details."
    }
    response = client.post(f"/api/tasks/{task_id}/review", json=reject_payload, headers=headers_mgr)
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    
    # Check that revision count is incremented and history contains the entry
    assert updated_task["revision_count"] == 1
    assert len(updated_task["revision_history"]) == 1
    entry = updated_task["revision_history"][0]
    assert entry["revision_number"] == 1
    assert entry["feedback"] == "Missing test coverage details."
    assert entry["rejected_by"] == "uid-mgr"
    
    # 6. Fetch task history (as Manager)
    response = client.get(f"/api/tasks/{task_id}/history", headers=headers_mgr)
    assert response.status_code == status.HTTP_200_OK
    history = response.json()
    assert history["task_id"] == task_id
    assert history["revision_count"] == 1
    assert len(history["revisions"]) == 1
    assert history["revisions"][0]["feedback"] == "Missing test coverage details."
    
    # 7. Fetch task history (as Employee - should fail 403)
    response = client.get(f"/api/tasks/{task_id}/history", headers=headers_emp)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_deadlines_and_overdue(client, setup_mocks):
    db = setup_mocks
    headers_mgr = {"Authorization": "Bearer manager-token"}
    headers_emp = {"Authorization": "Bearer employee-token"}

    now = datetime.now(timezone.utc)
    future_deadline = now + timedelta(days=2)
    past_deadline = now - timedelta(days=2)

    # 1. Create a task with a future deadline
    payload_future = {
        "title": "Task Future",
        "description": "Not overdue yet",
        "assigned_to": "uid-emp",
        "complexity": 1,
        "deadline": future_deadline.isoformat()
    }
    res = client.post("/api/tasks", json=payload_future, headers=headers_mgr)
    assert res.status_code == status.HTTP_201_CREATED
    task_future = res.json()
    assert task_future["is_overdue"] is False
    assert task_future["deadline"] is not None

    # 2. Create a task with a past deadline
    payload_past = {
        "title": "Task Past",
        "description": "Already overdue",
        "assigned_to": "uid-emp",
        "complexity": 2,
        "deadline": past_deadline.isoformat()
    }
    res = client.post("/api/tasks", json=payload_past, headers=headers_mgr)
    assert res.status_code == status.HTTP_201_CREATED
    task_past = res.json()
    assert task_past["is_overdue"] is True

    # 3. Get all tasks (as Employee) and check dynamic is_overdue
    res = client.get("/api/tasks", headers=headers_emp)
    assert res.status_code == status.HTTP_200_OK
    tasks = res.json()
    # Find Task Past
    t_past = next(t for t in tasks if t["title"] == "Task Past")
    assert t_past["is_overdue"] is True

    # 4. Get overdue tasks as Manager
    res = client.get("/api/tasks/overdue", headers=headers_mgr)
    assert res.status_code == status.HTTP_200_OK
    overdue_tasks = res.json()
    assert len(overdue_tasks) == 1
    assert overdue_tasks[0]["title"] == "Task Past"

    # 5. Get overdue tasks as Employee (should fail 403)
    res = client.get("/api/tasks/overdue", headers=headers_emp)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_audit_trail(client, setup_mocks):
    db = setup_mocks
    headers_mgr = {"Authorization": "Bearer manager-token"}
    headers_emp = {"Authorization": "Bearer employee-token"}

    # 1. Create a task (Manager)
    create_payload = {
        "title": "Audit Test Task",
        "description": "Verification of logging",
        "assigned_to": "uid-emp",
        "complexity": 3
    }
    res = client.post("/api/tasks", json=create_payload, headers=headers_mgr)
    assert res.status_code == status.HTTP_201_CREATED
    task = res.json()
    task_id = task["id"]

    # 2. Start the task (Employee)
    client.post(f"/api/tasks/{task_id}/start", headers=headers_emp)

    # 3. Submit the task (Employee)
    client.post(f"/api/tasks/{task_id}/submit", headers=headers_emp)

    # 4. Reject the task (Manager)
    reject_payload = {
        "action": "reject",
        "feedback": "Needs code cleanup."
    }
    client.post(f"/api/tasks/{task_id}/review", json=reject_payload, headers=headers_mgr)

    # 5. Query task audit trail (Manager)
    res = client.get(f"/api/tasks/{task_id}/audit", headers=headers_mgr)
    assert res.status_code == status.HTTP_200_OK
    audit_trail = res.json()
    
    assert len(audit_trail) == 4
    assert audit_trail[0]["action"] == "created"
    assert audit_trail[0]["new_stage"] == "todo"
    
    assert audit_trail[1]["action"] == "started"
    assert audit_trail[1]["previous_stage"] == "todo"
    assert audit_trail[1]["new_stage"] == "in_progress"
    
    assert audit_trail[2]["action"] == "submitted"
    assert audit_trail[2]["new_stage"] == "submitted_for_review"
    
    assert audit_trail[3]["action"] == "rejected"
    assert audit_trail[3]["new_stage"] == "in_progress"
    assert audit_trail[3]["details"] == "Needs code cleanup."

    # 6. Query recent audit logs (Manager)
    res = client.get("/api/audit/recent", headers=headers_mgr)
    assert res.status_code == status.HTTP_200_OK
    recent_logs = res.json()
    assert len(recent_logs) >= 4

    # 7. Query audit endpoints (Employee - should fail 403)
    res = client.get(f"/api/tasks/{task_id}/audit", headers=headers_emp)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    res = client.get("/api/audit/recent", headers=headers_emp)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_workload_dashboard(client, setup_mocks):
    db = setup_mocks
    headers_mgr = {"Authorization": "Bearer manager-token"}
    headers_emp = {"Authorization": "Bearer employee-token"}
    from bson import ObjectId

    # 1. Register a second employee in mock DB list directly
    db.data["users"].append({
        "_id": ObjectId(),
        "firebase_uid": "uid-emp2",
        "email": "emp2@test.com",
        "name": "Employee Two",
        "role": "employee"
    })

    # 2. Create tasks assigned to Test Employee (uid-emp)
    client.post("/api/tasks", json={
        "title": "Task 1",
        "assigned_to": "uid-emp",
        "complexity": 2
    }, headers=headers_mgr)

    res = client.post("/api/tasks", json={
        "title": "Task 2",
        "assigned_to": "uid-emp",
        "complexity": 3
    }, headers=headers_mgr)
    task2_id = res.json()["id"]

    # Start Task 2 so it enters in_progress
    client.post(f"/api/tasks/{task2_id}/start", headers=headers_emp)

    # 3. Get workload dashboard (Manager)
    res = client.get("/api/analytics/workload", headers=headers_mgr)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    employees = data["employees"]
    assert len(employees) == 2

    # Find stats for Employee One (uid-emp) and Employee Two (uid-emp2)
    emp1 = next(e for e in employees if e["firebase_uid"] == "uid-emp")
    emp2 = next(e for e in employees if e["firebase_uid"] == "uid-emp2")

    assert emp1["total_tasks"] == 2
    assert emp1["weighted_load"] == 5
    assert emp1["by_stage"]["todo"]["count"] == 1
    assert emp1["by_stage"]["todo"]["weight"] == 2
    assert emp1["by_stage"]["in_progress"]["count"] == 1
    assert emp1["by_stage"]["in_progress"]["weight"] == 3

    assert emp2["total_tasks"] == 0
    assert emp2["weighted_load"] == 0
    assert emp2["by_stage"]["todo"]["count"] == 0
    assert emp2["by_stage"]["todo"]["weight"] == 0

    # 4. Try getting workload dashboard (Employee - should fail 403)
    res = client.get("/api/analytics/workload", headers=headers_emp)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_manager_completion_metrics(client, setup_mocks):
    db = setup_mocks
    headers_mgr = {"Authorization": "Bearer manager-token"}
    headers_emp = {"Authorization": "Bearer employee-token"}

    # 1. Create task (Manager)
    res = client.post("/api/tasks", json={
        "title": "Task Metrics",
        "assigned_to": "uid-emp",
        "complexity": 2
    }, headers=headers_mgr)
    task_id = res.json()["id"]

    # 2. Complete task cycle: start -> submit -> confirm
    client.post(f"/api/tasks/{task_id}/start", headers=headers_emp)
    client.post(f"/api/tasks/{task_id}/submit", headers=headers_emp)

    # We want to test time metrics, so let's adjust created_at in the mock db to 2 hours ago
    from datetime import datetime, timedelta, timezone
    for t in db.data["tasks"]:
        if str(t["_id"]) == task_id:
            t["created_at"] = datetime.now(timezone.utc) - timedelta(hours=2)

    # Confirm it
    client.post(f"/api/tasks/{task_id}/review", json={"action": "confirm"}, headers=headers_mgr)

    # 3. Create a second task that gets rejected once, then remains in_progress
    res = client.post("/api/tasks", json={
        "title": "Task Metrics 2",
        "assigned_to": "uid-emp",
        "complexity": 3
    }, headers=headers_mgr)
    task2_id = res.json()["id"]
    client.post(f"/api/tasks/{task2_id}/start", headers=headers_emp)
    client.post(f"/api/tasks/{task2_id}/submit", headers=headers_emp)
    client.post(f"/api/tasks/{task2_id}/review", json={"action": "reject", "feedback": "Fix this"}, headers=headers_mgr)

    # 4. Fetch metrics (Manager)
    res = client.get("/api/analytics/metrics", headers=headers_mgr)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    # Check overall stats
    overall = data["overall"]
    assert overall["total_tasks"] == 2
    assert overall["completed"] == 1
    assert overall["completion_rate"] == 0.5
    # avg_completion_time_hours should be around 2.0 (allow slight offset)
    assert 1.9 <= overall["avg_completion_time_hours"] <= 2.1
    # One task rejected out of two total -> 0.5 rejection rate
    assert overall["rejection_rate"] == 0.5

    # Check per-employee stats
    assert len(data["per_employee"]) == 1
    emp_stats = data["per_employee"][0]
    assert emp_stats["name"] == "Test Employee"
    assert emp_stats["total"] == 2
    assert emp_stats["completed"] == 1
    assert emp_stats["completion_rate"] == 0.5
    assert 1.9 <= emp_stats["avg_completion_time_hours"] <= 2.1
    assert emp_stats["rejection_rate"] == 0.5
    assert emp_stats["complexity_distribution"] == {"1": 0, "2": 1, "3": 1}

    # 5. Fetch metrics (Employee - should fail 403)
    res = client.get("/api/analytics/metrics", headers=headers_emp)
    assert res.status_code == status.HTTP_403_FORBIDDEN



