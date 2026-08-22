# System Architecture & Technical Design

> **Foreman Kanban** — Collaborative Task Management & DevOps Simulation System

---

## 1. High-Level System Architecture

Foreman Kanban is structured as a decoupled, multi-tier cloud application comprising a single-page React frontend, a high-performance Python FastAPI backend, a MongoDB document store, and Firebase Authentication for identity management.

```
+-------------------------------------------------------------------------+
|                              PRESENTATION LAYER                         |
|  Vercel Hosting                                                         |
|  React 19 + Vite 8 SPA | Foreman Design System Tokens (Vanilla CSS)      |
+------------------------------------+------------------------------------+
                                     |
                                     | REST API + Bearer ID Token
                                     v
+-------------------------------------------------------------------------+
|                              APPLICATION LAYER                          |
|  Render Hosting                                                         |
|  Python 3.12 + FastAPI | Pydantic Schemas | Firebase Admin SDK Verification|
|  Role Guard Middleware | Status Transition Engine                        |
+------------------------------------+------------------------------------+
                                     |
                                     | Async Driver (Motor)
                                     v
+-------------------------------------------------------------------------+
|                                DATA LAYER                               |
|  MongoDB Atlas (M0 Free Cluster)                                        |
|  Collections: users (roles & profiles), tasks (Kanban state & feedback) |
+-------------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Frontend (Single Page Application)
- **Framework:** React 19 bootstrapped with Vite 8.
- **State & Context:** `AuthContext` wraps the app to provide reactive authentication state, current user profile, and role (`manager` vs `employee`). `ToastContext` provides global notification toasts.
- **Role-Aware Dashboards:**
  - `ManagerDashboard`: Renders the full Kanban board across all stages, the Manager Inspection Queue ("PR Inbox"), and the "New Work Order" modal trigger.
  - `EmployeeDashboard`: Filters board items to show only tasks assigned to the authenticated employee, providing quick action buttons ("Start Job", "Submit for Inspection").
- **Design System:** Custom Vanilla CSS based on industrial UI tokens:
  - Dark panel background (`#15130F`)
  - Amber highlight color (`#E8A23D`)
  - Paper ticket texture (`#FAF6EC`)
  - Stamp overlays for approval (`APPROVED`) and rejection (`SENT BACK`).

### 2.2 Backend (REST API)
- **Framework:** FastAPI (Python 3.12) running under Uvicorn ASGI server.
- **Authentication & Authorization:**
  - `firebase_auth.py`: Initializes Firebase Admin SDK (supporting both local `serviceAccountKey.json` and cloud `FIREBASE_SERVICE_ACCOUNT_JSON` environment variables) and validates incoming Bearer tokens.
  - `role_guard.py`: A FastAPI dependency factory `require_role(role)` that resolves the authenticated Firebase UID against MongoDB `users` and enforces role-based access control (RBAC).
- **Core Domain State Machine (`status_machine.py`):** Encapsulates task lifecycle transitions and authorization rules.

### 2.3 Database Tier
- **Engine:** MongoDB Atlas (M0 Free Tier) connected asynchronously via `Motor` (`AsyncIOMotorClient`).
- **Collections:**
  - `users`: `{ firebase_uid, email, name, role }`
  - `tasks`: `{ _id, title, description, assigned_to, complexity, stage, is_rejected, rejection_feedback, created_by, created_at, updated_at }`

---

## 3. Core Task Lifecycle & State Machine

The task lifecycle mirrors software development Pull-Request review and merge cycles:

```
 [ TO DO ] ------------(Employee Starts)------------> [ IN PROGRESS ]
                                                            |
                                                            | (Employee Submits)
                                                            v
 [ SIGNED OFF ] <-------(Manager Approves)------ [ FOR INSPECTION ]
                                                            |
                                                            | (Manager Rejects + Feedback)
                                                            +-------------------------------+
```

### Transition Rule Table

| From Stage | To Stage | Authorized Role | Action | Rejection Feedback |
|------------|----------|-----------------|--------|---------------------|
| `todo` | `in_progress` | Employee | Start Job | Cleared |
| `in_progress` | `submitted_for_review` | Employee | Submit for Inspection | Cleared |
| `submitted_for_review` | `done` | Manager | Confirm (Approve) | Cleared |
| `submitted_for_review` | `in_progress` | Manager | Send Back (Reject) | Required |

*Note: `done` ("Signed Off") is a terminal state. Tasks in `done` state cannot be moved.*

---

## 4. DevOps & Cloud Infrastructure

### 4.1 Multi-Stage Containerization
- **Backend Dockerfile:**
  - Stage 1 (`builder`): Installs dependencies into a virtualenv (`/opt/venv`).
  - Stage 2 (`production`): Uses `python:3.12-slim`, runs as non-root user `foreman`, and executes `uvicorn app.main:app`.
- **Frontend Dockerfile:**
  - Stage 1 (`builder`): Compiles React static bundle with Vite.
  - Stage 2 (`production`): Serves static bundle using `nginx:1.25-alpine` configured for SPA routing and API reverse proxying.

### 4.2 Local Orchestration (Docker Compose)
`docker-compose.yml` orchestrates three services:
1. `mongo`: MongoDB 7 container with persistent volume `foreman-mongo-data`.
2. `backend`: FastAPI backend connected via Docker network `foreman-network`.
3. `frontend`: Nginx frontend exposing port 80.

### 4.3 Kubernetes Learning Manifests (`k8s/`)
Configured for minikube local cluster deployments:
- `namespace.yml`: Creates `foreman` namespace.
- `configmap.yml` & `secrets.yml`: Manages environment configuration.
- `mongo-pv.yml` & `mongo-deployment.yml`: Local database deployment with PVC.
- `backend-deployment.yml` & `frontend-deployment.yml`: App deployments with health probes.
- `ingress.yml`: Ingress controller rules.
- `hpa.yml`: Horizontal Pod Autoscaler based on CPU usage.

---

## 5. Security Architecture

1. **Token Verification:** All mutation endpoints require a valid Firebase JWT ID Token issued by Firebase Auth.
2. **Strict Server-Side Authorization:** Role validation is performed exclusively on the server (`require_role` middleware), preventing client-side bypass.
3. **Pydantic Validation:** Strict input parsing limits title lengths, complexity values, and role options.
4. **Environment Isolation:** Credentials and database URIs are loaded dynamically from environment variables, preventing hardcoded secrets.
