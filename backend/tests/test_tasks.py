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
