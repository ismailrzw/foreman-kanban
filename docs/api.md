# Foreman API Reference

> RESTful API documentation for the **Foreman Kanban** backend.  
> Base Production URL: `https://foreman-api.onrender.com` (or local `http://localhost:8000`)

---

## Authentication & Headers

All protected endpoints require a valid Firebase ID Token passed in the `Authorization` header:

```http
Authorization: Bearer <FIREBASE_ID_TOKEN>
Content-Type: application/json
```

---

## 1. Health Endpoint

### `GET /api/health`
Public endpoint used by container health checks and Kubernetes liveness/readiness probes.

- **Auth Required:** No
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "service": "foreman-backend"
  }
  ```

---

## 2. Authentication & User Profile Routes

### `POST /api/register`
Links a newly created Firebase Auth user to a role (`manager` or `employee`) in MongoDB.

- **Auth Required:** Yes
- **Request Body (`UserCreate`):**
  ```json
  {
    "firebase_uid": "string",
    "email": "user@example.com",
    "name": "Display Name",
    "role": "manager" | "employee"
  }
  ```
- **Response `201 Created` (`UserResponse`):**
  ```json
  {
    "firebase_uid": "string",
    "email": "user@example.com",
    "name": "Display Name",
    "role": "manager"
  }
  ```
- **Errors:**
  - `403 Forbidden`: `firebase_uid` in body does not match decoded Bearer token.
  - `409 Conflict`: User already registered.

---

### `GET /api/me`
Retrieves the authenticated user's profile and assigned role.

- **Auth Required:** Yes
- **Response `200 OK` (`UserResponse`):**
  ```json
  {
    "firebase_uid": "string",
    "email": "user@example.com",
    "name": "Display Name",
    "role": "manager"
  }
  ```
- **Errors:**
  - `404 Not Found`: Profile not found in MongoDB.

---

### `GET /api/users/employees`
Lists all registered employees. Used by Managers to populate the "Assign to" dropdown when opening work orders.

- **Auth Required:** Yes (`Role: manager`)
- **Response `200 OK`:**
  ```json
  [
    {
      "firebase_uid": "emp_uid_1",
      "email": "saad@example.com",
      "name": "Saad Khan",
      "role": "employee"
    }
  ]
  ```

---

## 3. Task Management Routes

### `GET /api/tasks`
Lists tasks on the Kanban board.
- **Manager:** Sees ALL tasks across all employees.
- **Employee:** Sees ONLY tasks assigned to their `firebase_uid`.

- **Auth Required:** Yes
- **Response `200 OK` (`Array<TaskResponse>`):**
  ```json
  [
    {
      "id": "66b1a2f...",
      "title": "Fix Nginx Upstream Config",
      "description": "Adjust proxy pass headers",
      "assigned_to": "emp_uid_1",
      "assigned_to_name": "Saad Khan",
      "complexity": 2,
      "stage": "in_progress",
      "is_rejected": false,
      "rejection_feedback": null,
      "created_by": "mgr_uid_1",
      "created_at": "2026-08-05T20:00:00Z",
      "updated_at": "2026-08-05T20:15:00Z"
    }
  ]
  ```

---

### `POST /api/tasks`
Creates a new work order. Initial stage is always `todo`.

- **Auth Required:** Yes (`Role: manager`)
- **Request Body (`TaskCreate`):**
  ```json
  {
    "title": "Repair Pipeline Script",
    "description": "Fix docker push step in CD workflow",
    "assigned_to": "emp_uid_1",
    "complexity": 3
  }
  ```
- **Response `201 Created` (`TaskResponse`)**

---

### `POST /api/tasks/{task_id}/start`
Employee starts working on an assigned task.

- **Auth Required:** Yes (`Role: employee`)
- **Preconditions:** Task must be in `todo` stage and assigned to current user.
- **Effect:** Stage changes to `in_progress`.
- **Response `200 OK` (`TaskResponse`)**

---

### `POST /api/tasks/{task_id}/submit`
Employee submits completed work for Manager inspection (PR creation analog).

- **Auth Required:** Yes (`Role: employee`)
- **Preconditions:** Task must be in `in_progress` stage and assigned to current user.
- **Effect:** Stage changes to `submitted_for_review`.
- **Response `200 OK` (`TaskResponse`)**

---

### `POST /api/tasks/{task_id}/review`
Manager reviews a submitted task, confirming (approving/merging) or rejecting (requesting changes).

- **Auth Required:** Yes (`Role: manager`)
- **Preconditions:** Task must be in `submitted_for_review` stage.
- **Request Body (`TaskReviewAction`):**
  ```json
  {
    "action": "confirm" | "reject",
    "feedback": "Reason for rejection (Required if action=reject)"
  }
  ```
- **Effects:**
  - `action=confirm`: Stage becomes `done` ("Signed Off").
  - `action=reject`: Stage becomes `in_progress`, `is_rejected=true`, `rejection_feedback` set.
- **Response `200 OK` (`TaskResponse`)**

---

### `PUT /api/tasks/{task_id}`
Updates task metadata (title, description, complexity, assignee).

- **Auth Required:** Yes (`Role: manager`)
- **Response `200 OK` (`TaskResponse`)**

---

### `DELETE /api/tasks/{task_id}`
Deletes a task work order.

- **Auth Required:** Yes (`Role: manager`)
- **Response `204 No Content`**
