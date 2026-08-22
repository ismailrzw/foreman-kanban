# FOREMAN — Collaborative Kanban Task Board (Trello-Lite)

## Role-Based, Multi-User, Cloud-Deployed Edition — Complete DevOps Simulation

> **University DevOps Project — Semester 6**
> **Team:** Ismail (Lead/Integration), Ibrahim (Backend), Saad (Frontend)

---

> [!NOTE]
> **UI Design Language:** This project uses the "Foreman" industrial aesthetic — dark panels (`#15130F`), amber accents (`#E8A23D`), paper-textured ticket cards (`#FAF6EC`), Oswald + Inter + Courier Prime typography, pin-board metaphor with stamp animations for approval/rejection. All screens (auth, manager dashboard, employee dashboard, modals, toasts) follow this design system. Reference the `foreman-prototype.html` for exact CSS tokens and component patterns.

---

## Table of Contents

- [Phase 0 — Bare Repository & Directory Structure](#phase-0--bare-repository--directory-structure)
- [Phase 1 — Base MVP Application](#phase-1--base-mvp-application-starter-code)
- [Phase 2 — Architecture Design](#phase-2--architecture-design)
- [Phase 3 — Git Workflow (Strict)](#phase-3--git-workflow-strict)
- [Phase 4 — Local Dev Environment Setup](#phase-4--local-dev-environment-setup-all-members)
- [Phase 5 — Individual DevOps Responsibility Model](#phase-5--individual-devops-responsibility-model)
- [Phase 6 — Feature Increments (5 Per Person)](#phase-6--feature-increments-5-per-person--large-substantial-features)
- [Phase 7 — Docker (All Members)](#phase-7--docker-all-members-same-toolset)
- [Phase 8 — Security, Auth & RBAC Deep Dive](#phase-8--security-auth--rbac-deep-dive)
- [Phase 9 — CI/CD Pipeline (GitHub Actions)](#phase-9--cicd-pipeline-github-actions)
- [Phase 10 — Kubernetes (Local Learning Cluster)](#phase-10--kubernetes-local-learning-cluster)
- [Phase 11 — Free Cloud Deployment](#phase-11--free-cloud-deployment-multi-user-public-access)
- [Phase 12 — Submission & Evaluation](#phase-12--submission--evaluation)

---

## Team Structure & Role Clarification

> [!IMPORTANT]
> There are **two completely separate role systems** in this project. Confusing them is the #1 source of misunderstandings.

### Development Team Roles (Students)

| Student | Dev Role | Owns | Merge Rights |
|---------|----------|------|--------------|
| **Ismail** | Team Lead / Integration & Release Engineer | Repo structure, branch protection, Docker Compose, K8s manifests, CI/CD pipeline, cloud deployment | **ONLY person who merges PRs** |
| **Ibrahim** | Backend Engineer & Backend DevOps Operator | FastAPI code, backend Dockerfile, role-enforcement middleware, task status-machine logic | None — opens PRs to Ismail |
| **Saad** | Frontend Engineer & Frontend DevOps Operator | React code, Firebase Auth UI, role-aware dashboards, frontend Dockerfile | None — opens PRs to Ismail |

### Application Roles (End Users)

| App Role | Can Do | Cannot Do |
|----------|--------|-----------|
| **Manager** | Create tasks, assign to employees, set complexity, advance stages, confirm/reject submissions | N/A — full access |
| **Employee** | View own tasks, start jobs, submit for inspection (like opening a PR) | Create/assign/delete tasks, self-approve, see other employees' tasks |

**All three students** create test accounts of **both** app-roles to validate the system end-to-end.

---

## Application Stack

| Layer | Technology | Cloud (Free Tier) |
|-------|-----------|-------------------|
| Frontend | React (Vite) | Vercel |
| Backend | Python FastAPI | Render |
| Database | MongoDB | MongoDB Atlas (M0 Free) |
| Auth | Firebase Authentication (Email/Password + email verification) | Firebase (free Spark plan) |
| Local DevOps | Git + GitHub, Docker, Docker Compose, Kubernetes (minikube) | — |
| CI/CD | GitHub Actions | GitHub Free (2,000 mins/month) |

---

# PHASE 0 — Bare Repository & Directory Structure

**Owner:** Ismail creates this structure and pushes it to GitHub.

## 0.1 — Create the Repository

```bash
# Ismail runs these commands
mkdir foreman-kanban && cd foreman-kanban
git init
```

## 0.2 — Full Directory Tree

```
foreman-kanban/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # GitHub Actions — CI on PR
│   │   └── cd.yml                    # GitHub Actions — CD on merge to main
│   └── PULL_REQUEST_TEMPLATE.md      # PR template for consistency
│
├── backend/
│   ├── app/
│   │   ├── __init__.py               # Package marker
│   │   ├── main.py                   # FastAPI app entry point, CORS config
│   │   ├── config.py                 # Environment variable loading (Mongo URI, Firebase, etc.)
│   │   ├── firebase_auth.py          # Firebase Admin SDK init + token verification middleware
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User model (firebase_uid, email, name, role)
│   │   │   └── task.py               # Task model (title, desc, complexity, stage, status, assigned_to, etc.)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py        # POST /register (creates user doc with role after Firebase signup)
│   │   │   ├── task_routes.py        # Full CRUD + assign + confirm/reject + submit-for-review
│   │   │   └── user_routes.py        # GET /users (manager-only: list employees for assignment dropdown)
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── role_guard.py         # require_role("manager") / require_role("employee") dependency
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── status_machine.py     # Task status transition validation (the core state machine)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_tasks.py             # Unit tests for task CRUD + status transitions
│   │   └── test_auth.py              # Unit tests for role guard middleware
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Multi-stage Dockerfile for backend
│   ├── .env.example                  # Template env vars (never committed with real values)
│   └── .dockerignore
│
├── frontend/
│   ├── public/
│   │   └── index.html                # Vite entry HTML
│   ├── src/
│   │   ├── main.jsx                  # React entry point
│   │   ├── App.jsx                   # Root component with routing
│   │   ├── index.css                 # Global styles — Foreman design system tokens
│   │   ├── firebase.js               # Firebase client SDK init
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx       # React context for Firebase auth state + user role
│   │   ├── components/
│   │   │   ├── AuthScreen.jsx        # Login / Signup with role selection (Clock In / New Hire tabs)
│   │   │   ├── Topbar.jsx            # Sticky nav bar with brand, user badge, logout
│   │   │   ├── TicketCard.jsx        # Paper-style ticket with pin, complexity dots, stamp animations
│   │   │   ├── BoardColumn.jsx       # Kanban column (To Do / In Progress / For Inspection / Done)
│   │   │   ├── InspectionQueue.jsx   # Manager's pending-review list (PR inbox style)
│   │   │   ├── NewTaskModal.jsx      # Modal form for creating work orders
│   │   │   ├── RejectPanel.jsx       # Inline rejection textarea with feedback
│   │   │   └── Toast.jsx             # Bottom-center notification toast
│   │   ├── pages/
│   │   │   ├── ManagerDashboard.jsx  # Board + inspection queue + "New Work Order" button
│   │   │   └── EmployeeDashboard.jsx # Filtered board (own tasks only) + submit actions
│   │   └── utils/
│   │       └── api.js                # Axios instance with Firebase token injection
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile                    # Multi-stage Dockerfile (build → Nginx)
│   ├── nginx.conf                    # Nginx config for SPA routing + API proxy
│   ├── .env.example
│   └── .dockerignore
│
├── k8s/
│   ├── namespace.yml                 # foreman namespace
│   ├── configmap.yml                 # Non-secret config (API URL, frontend URL)
│   ├── secrets.yml                   # Template — Mongo URI, Firebase service account (base64)
│   ├── backend-deployment.yml        # Backend Deployment + Service
│   ├── frontend-deployment.yml       # Frontend Deployment + Service
│   ├── mongo-deployment.yml          # Local MongoDB Deployment + Service + PVC
│   ├── mongo-pv.yml                  # PersistentVolume for local Mongo data
│   ├── ingress.yml                   # Ingress for local cluster routing
│   └── hpa.yml                       # HorizontalPodAutoscaler (Phase 6 feature)
│
├── docker-compose.yml                # Full-stack local dev (backend + frontend + mongo)
├── .gitignore                        # Comprehensive gitignore
├── .env.example                      # Root-level env template
└── README.md                         # Project overview + setup instructions
```

## 0.3 — Folder Purpose Explanations

| Folder | Purpose |
|--------|---------|
| `.github/workflows/` | GitHub Actions CI/CD pipeline definitions. `ci.yml` runs on every PR (lint, test, build). `cd.yml` runs on merge to `main` (build, push to DockerHub, trigger cloud deploy). |
| `backend/app/` | FastAPI application code. Organized by concern: models (data shapes), routes (API endpoints), middleware (auth/role guards), utils (shared logic like the status machine). |
| `backend/app/middleware/` | Contains `role_guard.py` — the `require_role()` FastAPI dependency that checks the authenticated user's role on every protected route. This is where **server-side authorization** lives. |
| `backend/app/utils/status_machine.py` | The **core feature**: validates legal status transitions (e.g., only `in_progress` → `submitted_for_review`, only a Manager can transition `submitted_for_review` → `done`). This is the PR-review-merge analog. |
| `backend/tests/` | Unit tests for task CRUD, status transitions, and auth middleware. CI pipeline runs these on every PR. |
| `frontend/src/contexts/` | React Context for Firebase auth state. Provides `currentUser`, `role`, `token`, and `loading` state to all components. |
| `frontend/src/components/` | Reusable UI components following the Foreman design system — paper tickets with pins, stamp animations, industrial color palette. |
| `frontend/src/pages/` | Page-level components: `ManagerDashboard` (full board + inspection queue) vs `EmployeeDashboard` (filtered board + submit actions). Role-aware routing renders the correct page. |
| `k8s/` | Kubernetes manifests for local learning cluster deployment. Each team member deploys these to their own minikube cluster independently. |

## 0.4 — Skeleton Files

Ismail creates all files as empty placeholders (or with minimal boilerplate) so the directory structure exists in Git from day one:

```bash
# From the repo root — create all directories
mkdir -p .github/workflows
mkdir -p backend/app/models backend/app/routes backend/app/middleware backend/app/utils
mkdir -p backend/tests
mkdir -p frontend/public frontend/src/contexts frontend/src/components frontend/src/pages frontend/src/utils
mkdir -p k8s

# Create all placeholder files
touch .github/workflows/ci.yml .github/workflows/cd.yml .github/PULL_REQUEST_TEMPLATE.md
touch backend/app/__init__.py backend/app/main.py backend/app/config.py backend/app/firebase_auth.py
touch backend/app/models/__init__.py backend/app/models/user.py backend/app/models/task.py
touch backend/app/routes/__init__.py backend/app/routes/auth_routes.py backend/app/routes/task_routes.py backend/app/routes/user_routes.py
touch backend/app/middleware/__init__.py backend/app/middleware/role_guard.py
touch backend/app/utils/__init__.py backend/app/utils/status_machine.py
touch backend/tests/__init__.py backend/tests/test_tasks.py backend/tests/test_auth.py
touch backend/requirements.txt backend/Dockerfile backend/.env.example backend/.dockerignore
touch frontend/src/main.jsx frontend/src/App.jsx frontend/src/index.css frontend/src/firebase.js
touch frontend/src/contexts/AuthContext.jsx
touch frontend/src/components/AuthScreen.jsx frontend/src/components/Topbar.jsx
touch frontend/src/components/TicketCard.jsx frontend/src/components/BoardColumn.jsx
touch frontend/src/components/InspectionQueue.jsx frontend/src/components/NewTaskModal.jsx
touch frontend/src/components/RejectPanel.jsx frontend/src/components/Toast.jsx
touch frontend/src/pages/ManagerDashboard.jsx frontend/src/pages/EmployeeDashboard.jsx
touch frontend/src/utils/api.js
touch frontend/vite.config.js frontend/Dockerfile frontend/nginx.conf frontend/.env.example frontend/.dockerignore
touch k8s/namespace.yml k8s/configmap.yml k8s/secrets.yml
touch k8s/backend-deployment.yml k8s/frontend-deployment.yml
touch k8s/mongo-deployment.yml k8s/mongo-pv.yml k8s/ingress.yml k8s/hpa.yml
touch docker-compose.yml .env.example README.md
```

## 0.5 — `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg
.venv/
venv/
env/

# Node
node_modules/
frontend/node_modules/
frontend/dist/

# Environment files (NEVER commit real secrets)
.env
.env.local
.env.production
backend/.env
frontend/.env

# Firebase service account (CRITICAL — never commit)
**/serviceAccountKey.json
**/firebase-service-account.json
**/firebase-adminsdk*.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.log

# Kubernetes secrets with real values
k8s/secrets-real.yml
```

## 0.6 — Initial Commit & Push

```bash
git add -A
git commit -m "chore: scaffold bare repository structure — Phase 0"
git branch -M main
git remote add origin https://github.com/<your-org>/foreman-kanban.git
git push -u origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

---

# PHASE 1 — Base MVP Application (Starter Code)

> **Owner:** Ismail writes all of this, pushes to `develop`, then merges to `main`. Ibrahim and Saad clone after.

> [!IMPORTANT]
> Every file below is shown **in full** — no placeholders. This is the complete, working MVP that runs with `npm run dev` (frontend) and `uvicorn` (backend) before any Docker/K8s tooling.

---

## 1.1 — Firebase Project Setup (Ismail Does This First)

### Step 1: Create the Firebase Project

1. Go to [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Project name: `foreman-kanban`
4. Disable Google Analytics (not needed for this project) → **Create Project**
5. Wait for provisioning (~30 seconds) → Click **Continue**

### Step 2: Enable Email/Password Authentication

1. In the Firebase console sidebar, click **Build → Authentication**
2. Click **"Get started"**
3. Under **Sign-in method** tab, click **Email/Password**
4. Toggle **"Enable"** to ON
5. Toggle **"Email link (passwordless sign-in)"** to OFF (we want password-based)
6. Click **Save**

### Step 3: Enable Email Verification Flow

Firebase automatically supports email verification via `sendEmailVerification()` in the client SDK. No additional console setup needed — we'll enforce verification in the frontend by checking `user.emailVerified` after login.

### Step 4: Get Web App Config Keys (For Frontend)

1. In Firebase console, click the **gear icon** → **Project settings**
2. Scroll down to **"Your apps"** section → Click **web icon** (`</>`)
3. Register app with nickname: `foreman-frontend`
4. **Do NOT** enable Firebase Hosting (we'll use Vercel)
5. Copy the config object — it looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "foreman-kanban.firebaseapp.com",
  projectId: "foreman-kanban",
  storageBucket: "foreman-kanban.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

6. Save these values — they go into `frontend/.env`

### Step 5: Generate Backend Service Account JSON (For Backend Token Verification)

1. In Firebase console → **gear icon** → **Project settings** → **Service accounts** tab
2. Select **"Firebase Admin SDK"**
3. Language: **Python**
4. Click **"Generate new private key"** → Confirm
5. A JSON file downloads (e.g., `foreman-kanban-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`)
6. **Rename it** to `serviceAccountKey.json`
7. Place it in `backend/` folder — **NEVER commit this file** (it's already in `.gitignore`)
8. Share it with teammates **securely** (encrypted zip, private Slack DM — never paste in chat/email)

> [!CAUTION]
> The `serviceAccountKey.json` file is a **private key** that grants full admin access to your Firebase project. If committed to Git or leaked publicly, anyone can impersonate your backend. It's already in `.gitignore` — never override this.

---

## 1.2 — MongoDB Atlas Free Tier Setup (Ismail Does This)

### Step 1: Create MongoDB Atlas Account & Cluster

1. Go to [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas) → **Try Free**
2. Sign up with Google or email
3. After login → **Build a Database**
4. Select **M0 FREE** (Shared) tier
5. Cloud Provider: **AWS**
6. Region: Pick the closest to your team (e.g., `eu-central-1` Frankfurt or `us-east-1` Virginia)
7. Cluster Name: `foreman-cluster` → Click **Create**
8. Wait ~3 minutes for provisioning

### Step 2: Database Access (Create User)

1. In the left sidebar → **Database Access** → **Add New Database User**
2. Authentication Method: **Password**
3. Username: `foreman-admin`
4. Password: Click **Autogenerate Secure Password** → **Copy and save it somewhere safe**
5. Database User Privileges: **Atlas admin** (for simplicity in dev; scope down for production)
6. Click **Add User**

### Step 3: Network Access (Allow Connections)

1. Left sidebar → **Network Access** → **Add IP Address**
2. For development: Click **"Allow Access from Anywhere"** (`0.0.0.0/0`) — this is fine for a free dev cluster
3. Click **Confirm**

> [!WARNING]
> `0.0.0.0/0` allows any IP to connect. This is acceptable for a free-tier dev/learning project but never appropriate for production databases with sensitive data.

### Step 4: Get Connection String

1. Go to **Database** → Click **Connect** on your cluster
2. Choose **"Connect your application"**
3. Driver: **Python** / Version: **3.12 or later**
4. Copy the connection string — it looks like:

```
mongodb+srv://foreman-admin:<password>@foreman-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

5. Replace `<password>` with the password you saved in Step 2
6. Append the database name: `mongodb+srv://foreman-admin:YOUR_PASSWORD@foreman-cluster.xxxxx.mongodb.net/foreman_db?retryWrites=true&w=majority`
7. This is your `MONGO_URI` — save it for `.env` files

### Step 5: Create the Database

1. Click **Browse Collections** on your cluster
2. Click **"Add My Own Data"**
3. Database name: `foreman_db`
4. Collection name: `users`
5. Click **Create**
6. Then add another collection: click **+** next to `foreman_db` → Collection name: `tasks` → **Create**

---

## 1.3 — Backend: Full FastAPI Application

### `backend/requirements.txt`

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
motor==3.6.0
pymongo==4.10.1
python-dotenv==1.0.1
firebase-admin==6.6.0
pydantic==2.10.3
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
```

### `backend/.env.example`

```env
MONGO_URI=mongodb+srv://foreman-admin:YOUR_PASSWORD@foreman-cluster.xxxxx.mongodb.net/foreman_db?retryWrites=true&w=majority
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json
FRONTEND_URL=http://localhost:5173
```

> **Ismail:** Create `backend/.env` (not `.env.example`) with real values. **Never commit `.env`.**

### `backend/app/__init__.py`

```python
# Package marker — intentionally empty
```

### `backend/app/config.py`

```python
"""
Configuration module — loads environment variables with sensible defaults.
All secrets (Mongo URI, Firebase SA path) come from .env, never hardcoded.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/foreman_db")

# Firebase Admin SDK service account
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_PATH", "./serviceAccountKey.json"
)

# CORS — allowed frontend origin
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
```

### `backend/app/firebase_auth.py`

```python
"""
Firebase Admin SDK initialization and ID token verification.
This module:
1. Initializes the Firebase Admin SDK using the service account JSON
2. Provides a FastAPI dependency that extracts and verifies the Firebase ID token
   from the Authorization header, returning the decoded token (with uid, email, etc.)
"""

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import FIREBASE_SERVICE_ACCOUNT_PATH

# Initialize Firebase Admin SDK (runs once at import time)
cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# FastAPI security scheme — expects "Bearer <token>" in Authorization header
bearer_scheme = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency: extracts the Bearer token from the Authorization header,
    verifies it with Firebase Admin SDK, and returns the decoded token dict.

    Returns dict with keys: uid, email, email_verified, etc.
    Raises 401 if token is invalid/expired/missing.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token.",
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired. Please re-authenticate.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not verify credentials: {str(e)}",
        )
```

### `backend/app/models/__init__.py`

```python
# Package marker
```

### `backend/app/models/user.py`

```python
"""
User model — links a Firebase UID to an application-level role.
When a user signs up via Firebase Auth on the frontend, the frontend
calls POST /api/register which creates this document in MongoDB.
"""

from pydantic import BaseModel, Field
from typing import Literal


class UserCreate(BaseModel):
    """Schema for user registration request body."""
    firebase_uid: str = Field(..., description="Firebase Auth UID from the decoded token")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, description="Display name")
    role: Literal["manager", "employee"] = Field(..., description="Application role")


class UserResponse(BaseModel):
    """Schema for user data returned by the API."""
    firebase_uid: str
    email: str
    name: str
    role: Literal["manager", "employee"]


class UserInDB(BaseModel):
    """Internal representation stored in MongoDB."""
    firebase_uid: str
    email: str
    name: str
    role: Literal["manager", "employee"]
```

### `backend/app/models/task.py`

```python
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
    created_by: str
    created_at: datetime
    updated_at: datetime
```

### `backend/app/utils/__init__.py`

```python
# Package marker
```

### `backend/app/utils/status_machine.py`

```python
"""
Task Status Machine — the CORE FEATURE of the application.

This module enforces legal status transitions for tasks, analogous to a
Pull Request review/merge workflow:

  Employee submits work → Manager inspects → Manager confirms (merge) or rejects (request changes)

Legal transitions:
  todo              → in_progress         (Employee starts working)
  in_progress       → submitted_for_review (Employee submits for inspection)
  submitted_for_review → done             (Manager confirms/approves)
  submitted_for_review → in_progress      (Manager rejects — sends back for rework)

Illegal transitions (examples):
  todo → done                              (Can't skip steps)
  submitted_for_review → done BY EMPLOYEE  (Can't self-approve)
  done → anything                          (Done is terminal)
"""

from typing import Literal

# Define the allowed transitions as a dict: current_stage → set of valid next stages
ALLOWED_TRANSITIONS = {
    "todo": {"in_progress"},
    "in_progress": {"submitted_for_review"},
    "submitted_for_review": {"done", "in_progress"},  # done = confirm, in_progress = reject
    "done": set(),  # Terminal state — no transitions out
}

# Define WHO can trigger each transition
# Key: (from_stage, to_stage) → required role
TRANSITION_ROLES = {
    ("todo", "in_progress"): "employee",
    ("in_progress", "submitted_for_review"): "employee",
    ("submitted_for_review", "done"): "manager",          # Only manager can confirm
    ("submitted_for_review", "in_progress"): "manager",   # Only manager can reject
}


def validate_transition(
    current_stage: str,
    new_stage: str,
    user_role: Literal["manager", "employee"],
) -> tuple[bool, str]:
    """
    Validates whether a stage transition is legal for the given user role.

    Args:
        current_stage: The task's current stage
        new_stage: The proposed new stage
        user_role: The role of the user attempting the transition

    Returns:
        Tuple of (is_valid, error_message).
        If valid: (True, "")
        If invalid: (False, "Human-readable error explaining why")
    """
    # Check if the transition itself is legal
    allowed = ALLOWED_TRANSITIONS.get(current_stage, set())
    if new_stage not in allowed:
        return (
            False,
            f"Cannot move task from '{current_stage}' to '{new_stage}'. "
            f"Allowed transitions from '{current_stage}': {allowed or 'none (terminal state)'}.",
        )

    # Check if the user's role is authorized for this transition
    required_role = TRANSITION_ROLES.get((current_stage, new_stage))
    if required_role and required_role != user_role:
        return (
            False,
            f"Only a {required_role} can move a task from '{current_stage}' to '{new_stage}'. "
            f"You are logged in as a {user_role}.",
        )

    return (True, "")
```

### `backend/app/middleware/__init__.py`

```python
# Package marker
```

### `backend/app/middleware/role_guard.py`

```python
"""
Role-based access control middleware for FastAPI.

Provides `require_role()` — a dependency factory that:
1. Verifies the Firebase ID token (via verify_firebase_token)
2. Looks up the user's role in MongoDB
3. Checks that the role matches the required role
4. Returns the full user document if authorized, or 403 if not

Usage in routes:
    @router.post("/tasks", dependencies=[Depends(require_role("manager"))])
    async def create_task(...):
        ...

    # Or to get the user document:
    @router.get("/my-tasks")
    async def my_tasks(user=Depends(require_role("employee"))):
        # user is the full MongoDB user document
        ...
"""

from fastapi import Depends, HTTPException, status
from app.firebase_auth import verify_firebase_token
from app.main import get_database


def require_role(required_role: str = None):
    """
    Factory that returns a FastAPI dependency.
    If required_role is None, any authenticated user is allowed.
    If required_role is specified, only users with that role can access.
    """

    async def role_dependency(
        decoded_token: dict = Depends(verify_firebase_token),
    ) -> dict:
        """
        Inner dependency:
        1. Gets the Firebase UID from the decoded token
        2. Looks up the user in MongoDB
        3. Checks role if required
        4. Returns the user document
        """
        db = get_database()
        uid = decoded_token["uid"]

        # Look up user in MongoDB by Firebase UID
        user = await db.users.find_one({"firebase_uid": uid})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please complete registration first.",
            )

        # Check role if required
        if required_role and user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This endpoint requires the '{required_role}' role. "
                       f"Your role is '{user.get('role')}'.",
            )

        # Convert ObjectId to string for downstream use
        user["_id"] = str(user["_id"])
        return user

    return role_dependency
```

### `backend/app/routes/__init__.py`

```python
# Package marker
```

### `backend/app/routes/auth_routes.py`

```python
"""
Auth routes — handles user registration after Firebase signup.

Flow:
1. User signs up via Firebase Auth on the frontend (creates Firebase account)
2. Frontend calls POST /api/register with the Firebase ID token + chosen role
3. This route creates a user document in MongoDB linking Firebase UID → role
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.firebase_auth import verify_firebase_token
from app.models.user import UserCreate, UserResponse
from app.main import get_database

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    decoded_token: dict = Depends(verify_firebase_token),
):
    """
    Register a new user after Firebase signup.
    Links the Firebase UID to a role in MongoDB.

    - Requires a valid Firebase ID token in the Authorization header
    - The firebase_uid in the body must match the token's uid (security check)
    - Creates a user document in the 'users' collection
    """
    db = get_database()

    # Security check: the UID in the request body must match the authenticated token
    if user_data.firebase_uid != decoded_token["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token UID does not match the provided firebase_uid.",
        )

    # Check if user already exists
    existing = await db.users.find_one({"firebase_uid": user_data.firebase_uid})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered.",
        )

    # Insert into MongoDB
    user_doc = user_data.model_dump()
    await db.users.insert_one(user_doc)

    return UserResponse(**user_doc)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    decoded_token: dict = Depends(verify_firebase_token),
):
    """
    Get the currently authenticated user's profile.
    Used by the frontend to determine role after login.
    """
    db = get_database()
    user = await db.users.find_one({"firebase_uid": decoded_token["uid"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete registration.",
        )
    return UserResponse(**user)
```

### `backend/app/routes/user_routes.py`

```python
"""
User routes — manager-only endpoints for user management.
Primary use: populating the "Assign to" dropdown when creating tasks.
"""

from fastapi import APIRouter, Depends
from app.middleware.role_guard import require_role
from app.models.user import UserResponse
from app.main import get_database

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
```

### `backend/app/routes/task_routes.py`

```python
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
)
from app.utils.status_machine import validate_transition
from app.main import get_database

router = APIRouter(prefix="/api", tags=["tasks"])


def task_doc_to_response(doc: dict, users_cache: dict = None) -> TaskResponse:
    """Convert a MongoDB task document to a TaskResponse schema."""
    assigned_to_name = None
    if users_cache and doc.get("assigned_to") in users_cache:
        assigned_to_name = users_cache[doc["assigned_to"]]

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

    # Build update dict (only non-None fields)
    update_fields = {
        k: v for k, v in task_data.model_dump().items() if v is not None
    }

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

        await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "stage": "in_progress",
                "is_rejected": True,
                "rejection_feedback": review_data.feedback,
                "updated_at": now,
            }},
        )

    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return task_doc_to_response(updated)
```

### `backend/app/main.py`

```python
"""
FastAPI application entry point.
Configures CORS, connects to MongoDB, and registers all route modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from app.config import MONGO_URI, FRONTEND_URL

# ─── Database Connection ─────────────────────────────────────

_db_client: AsyncIOMotorClient = None
_database = None


def get_database():
    """Returns the MongoDB database instance. Used by routes and middleware."""
    return _database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager — connects to MongoDB on startup,
    disconnects on shutdown.
    """
    global _db_client, _database
    _db_client = AsyncIOMotorClient(MONGO_URI)
    _database = _db_client.get_default_database()
    print(f"✔ Connected to MongoDB: {_database.name}")
    yield
    _db_client.close()
    print("✔ MongoDB connection closed.")


# ─── FastAPI App ──────────────────────────────────────────────

app = FastAPI(
    title="Foreman API",
    description="Collaborative Kanban Task Board — Role-Based Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routes ─────────────────────────────────────────
# Import routes AFTER app creation to avoid circular imports

from app.routes.auth_routes import router as auth_router
from app.routes.task_routes import router as task_router
from app.routes.user_routes import router as user_router

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker/K8s probes."""
    return {"status": "healthy", "service": "foreman-backend"}
```

---

## 1.4 — Frontend: Full React Application

### Initialize Vite Project

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install firebase axios react-router-dom
```

### `frontend/.env.example`

```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=foreman-kanban.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=foreman-kanban
VITE_FIREBASE_STORAGE_BUCKET=foreman-kanban.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef123456
```

> **Ismail:** Create `frontend/.env` with real values. Share with team securely.

### `frontend/vite.config.js`

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### `frontend/public/index.html`

> Note: Vite uses `index.html` at the project root. Replace the default with:

### `frontend/index.html` (Root — Vite entry)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="Foreman — Collaborative Kanban Task Board with role-based approval workflow" />
  <title>Foreman — Assign the work. Inspect what's done.</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

### `frontend/src/main.jsx`

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### `frontend/src/index.css`

```css
/*
 * FOREMAN DESIGN SYSTEM
 * Industrial / workshop aesthetic — dark panels, amber accents,
 * paper-textured ticket cards, pin-board metaphor.
 *
 * Fonts: Oswald (display), Inter (body), Courier Prime (mono/codes)
 * Inspiration: foreman-prototype.html
 */

:root {
  --bg: #15130F;
  --bg-grid: #1B1812;
  --panel: #1E1B16;
  --panel-raised: #25211A;
  --hairline: #3A3528;
  --paper: #FAF6EC;
  --paper-shadow: rgba(0, 0, 0, 0.45);
  --ink: #2B2620;
  --ink-soft: #6B6354;
  --text: #ECE6D9;
  --text-muted: #9A9281;
  --stamp-red: #C1432A;
  --stamp-green: #4C7A4C;
  --amber: #E8A23D;
  --violet: #8C7BC9;
  --radius-card: 3px;
  --font-display: 'Oswald', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'Courier Prime', monospace;
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
}

body {
  font-family: var(--font-body);
  background-color: var(--bg);
  background-image: radial-gradient(circle, var(--bg-grid) 1.2px, transparent 1.2px);
  background-size: 26px 26px;
  color: var(--text);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::selection {
  background: var(--amber);
  color: var(--ink);
}

button {
  font-family: inherit;
  cursor: pointer;
}

input, select, textarea {
  font-family: inherit;
}

a {
  color: inherit;
  text-decoration: none;
}

:focus-visible {
  outline: 2px solid var(--amber);
  outline-offset: 2px;
}

/* ─── UTILITY CLASSES ─── */

.screen {
  display: none;
  min-height: 100vh;
}

.screen.active {
  display: flex;
  flex-direction: column;
}

/* ─── BUTTONS ─── */

.btn {
  border: none;
  font-family: var(--font-display);
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 13px;
  padding: 13px 20px;
  border-radius: 2px;
  transition: transform 0.08s ease, filter 0.15s ease;
  cursor: pointer;
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  background: var(--amber);
  color: var(--ink);
  font-weight: 600;
}

.btn-primary:hover {
  filter: brightness(1.08);
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--hairline);
  color: var(--text);
}

.btn-ghost:hover {
  border-color: var(--text-muted);
}

.btn-block {
  width: 100%;
  margin-top: 6px;
}

.btn-sm {
  font-size: 11px;
  padding: 8px 12px;
}

.btn-stamp-approve {
  background: var(--stamp-green);
  color: #fff;
}

.btn-stamp-reject {
  background: transparent;
  border: 1px solid var(--stamp-red);
  color: var(--stamp-red);
}

/* ─── AUTH SCREEN ─── */

.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
}

.auth-wrap {
  width: 100%;
  max-width: 980px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  border: 1px solid var(--hairline);
  background: var(--panel);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
}

@media (max-width: 800px) {
  .auth-wrap {
    grid-template-columns: 1fr;
  }
  .auth-side {
    display: none;
  }
}

.auth-side {
  padding: 48px 40px;
  background:
    repeating-linear-gradient(135deg, rgba(232, 162, 61, 0.05) 0 2px, transparent 2px 14px),
    var(--panel-raised);
  border-right: 1px solid var(--hairline);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark .rivet {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.3), 0 0 0 3px rgba(232, 162, 61, 0.15);
}

.brand-mark span {
  font-family: var(--font-display);
  font-size: 22px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.auth-side h1 {
  font-family: var(--font-display);
  font-size: 42px;
  line-height: 1.08;
  font-weight: 600;
  margin-top: 60px;
  letter-spacing: 0.5px;
}

.auth-side p {
  margin-top: 18px;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.6;
  max-width: 38ch;
}

.ledger {
  margin-top: 40px;
  border-top: 1px dashed var(--hairline);
  padding-top: 18px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ledger b {
  color: var(--amber);
}

.auth-form-area {
  padding: 48px 44px;
  display: flex;
  flex-direction: column;
}

.auth-tabs {
  display: flex;
  border: 1px solid var(--hairline);
  margin-bottom: 32px;
}

.auth-tab {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 1.5px;
  font-size: 13px;
  text-transform: uppercase;
  padding: 12px 0;
  border-right: 1px solid var(--hairline);
  cursor: pointer;
  transition: background 0.15s ease;
}

.auth-tab:last-child {
  border-right: none;
}

.auth-tab.is-active {
  background: var(--amber);
  color: var(--ink);
  font-weight: 600;
}

/* ─── FORM FIELDS ─── */

.field {
  margin-bottom: 18px;
}

.field label {
  display: block;
  font-size: 11px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 7px;
  font-weight: 600;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--hairline);
  color: var(--text);
  padding: 11px 12px;
  font-size: 14px;
  border-radius: 2px;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: var(--amber);
  outline: none;
}

.field-error {
  font-size: 12px;
  color: var(--stamp-red);
  margin-top: 6px;
  font-family: var(--font-mono);
}

.field.has-error input {
  border-color: var(--stamp-red);
}

/* ─── ROLE PICKER ─── */

.role-pick {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.role-opt {
  border: 1px solid var(--hairline);
  background: var(--bg);
  padding: 14px 12px;
  text-align: left;
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.role-opt b {
  display: block;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 14px;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.role-opt small {
  font-size: 11px;
  line-height: 1.4;
  display: block;
}

.role-opt.is-selected {
  border-color: var(--amber);
  background: rgba(232, 162, 61, 0.08);
}

.role-opt.is-selected b {
  color: var(--amber);
}

.auth-foot {
  margin-top: auto;
  padding-top: 24px;
  font-size: 12px;
  color: var(--text-muted);
}

/* ─── TOPBAR ─── */

.topbar {
  border-bottom: 1px solid var(--hairline);
  background: var(--panel);
  padding: 14px 28px;
  display: flex;
  align-items: center;
  gap: 24px;
  position: sticky;
  top: 0;
  z-index: 20;
}

.topbar .brand-mark span {
  font-size: 18px;
}

.topbar-divider {
  width: 1px;
  height: 26px;
  background: var(--hairline);
}

.topbar-title {
  font-family: var(--font-display);
  font-size: 13px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text-muted);
}

.topbar-spacer {
  flex: 1;
}

.id-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--hairline);
  padding: 6px 12px 6px 6px;
  background: var(--panel-raised);
}

.id-badge .avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  background: var(--amber);
  color: var(--ink);
}

.id-badge.role-employee .avatar {
  background: var(--violet);
  color: #15130F;
}

.id-badge .meta {
  line-height: 1.25;
}

.id-badge .meta b {
  font-size: 12.5px;
  display: block;
}

.id-badge .meta small {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.icon-btn {
  background: none;
  border: 1px solid var(--hairline);
  color: var(--text-muted);
  width: 34px;
  height: 34px;
  border-radius: 2px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.icon-btn:hover {
  color: var(--text);
  border-color: var(--text-muted);
}

/* ─── CONTENT AREA ─── */

.content {
  padding: 28px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 26px;
  gap: 16px;
  flex-wrap: wrap;
}

.page-head h2 {
  font-family: var(--font-display);
  font-size: 28px;
  letter-spacing: 0.5px;
}

.page-head p {
  color: var(--text-muted);
  font-size: 13.5px;
  margin-top: 4px;
}

/* ─── INSPECTION QUEUE ─── */

.queue-section {
  margin-bottom: 34px;
}

.queue-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.queue-section-head h3 {
  font-family: var(--font-display);
  font-size: 14px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.count-pill {
  background: var(--amber);
  color: var(--ink);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.queue-item {
  background: var(--panel-raised);
  border: 1px solid var(--hairline);
  border-left: 3px solid var(--amber);
  padding: 14px 16px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.queue-item .qi-main {
  flex: 1;
  min-width: 220px;
}

.queue-item .qi-main .qi-title {
  font-weight: 600;
  font-size: 14.5px;
}

.queue-item .qi-main .qi-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 3px;
  font-family: var(--font-mono);
}

.queue-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.reject-panel {
  width: 100%;
  margin-top: 12px;
  border-top: 1px dashed var(--hairline);
  padding-top: 12px;
}

.reject-panel textarea {
  width: 100%;
  min-height: 64px;
  background: var(--bg);
  border: 1px solid var(--hairline);
  color: var(--text);
  padding: 9px;
  font-size: 13px;
  border-radius: 2px;
  resize: vertical;
}

.reject-panel .reject-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.empty-queue {
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
  padding: 14px;
  border: 1px dashed var(--hairline);
  text-align: center;
}

/* ─── KANBAN BOARD ─── */

.board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

@media (max-width: 1100px) {
  .board {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .board {
    grid-template-columns: 1fr;
  }
}

.column {
  background: var(--panel);
  border: 1px solid var(--hairline);
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.column-head {
  padding: 12px 14px;
  border-bottom: 1px solid var(--hairline);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.column-head h4 {
  font-family: var(--font-display);
  font-size: 12px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text-muted);
}

.column-head .n {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

.column-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
}

.column-empty {
  color: var(--text-muted);
  font-size: 12px;
  font-style: italic;
  text-align: center;
  padding: 18px 6px;
}

/* ─── TICKET CARD (Paper style) ─── */

.ticket {
  position: relative;
  background: var(--paper);
  color: var(--ink);
  padding: 16px 14px 14px;
  box-shadow: 0 6px 14px var(--paper-shadow);
  border-radius: var(--radius-card);
  transition: transform 0.15s ease;
}

.ticket:nth-child(odd) {
  transform: rotate(-0.6deg);
}

.ticket:nth-child(even) {
  transform: rotate(0.6deg);
}

.ticket:hover {
  transform: rotate(0deg) translateY(-2px);
}

.ticket .pin {
  position: absolute;
  top: -7px;
  left: 16px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #ff8a3d, #b5460f);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.5);
}

.ticket.is-rework .pin {
  background: radial-gradient(circle at 35% 30%, #ff6e6e, #971f1f);
}

.ticket-id {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-soft);
  letter-spacing: 0.5px;
}

.ticket-title {
  font-family: var(--font-display);
  font-size: 15.5px;
  font-weight: 600;
  margin-top: 4px;
  line-height: 1.25;
}

.ticket-desc {
  font-size: 12.5px;
  color: var(--ink-soft);
  margin-top: 6px;
  line-height: 1.45;
}

.ticket-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  border-top: 1px dashed rgba(43, 38, 32, 0.25);
  padding-top: 10px;
}

.complexity-dots {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 2px;
}

.complexity-dots .filled {
  color: var(--stamp-red);
}

.complexity-dots .empty {
  color: rgba(43, 38, 32, 0.2);
}

.ticket-assignee {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ticket-assignee .mini-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--violet);
  color: #15130F;
  font-family: var(--font-display);
  font-size: 9px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ticket-assignee span {
  font-size: 11px;
  color: var(--ink-soft);
}

.rework-note {
  margin-top: 10px;
  background: rgba(193, 67, 42, 0.08);
  border-left: 2px solid var(--stamp-red);
  padding: 8px 10px;
  font-size: 11.5px;
  color: var(--ink);
  line-height: 1.4;
}

.rework-note b {
  display: block;
  font-size: 9.5px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--stamp-red);
  margin-bottom: 3px;
  font-family: var(--font-mono);
}

.ticket-action {
  margin-top: 12px;
  width: 100%;
  background: var(--ink);
  color: var(--paper);
  border: none;
  font-family: var(--font-display);
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 11px;
  padding: 9px 0;
  border-radius: 2px;
  cursor: pointer;
}

.ticket-action:hover {
  filter: brightness(1.3);
}

.ticket-action.is-disabled {
  background: transparent;
  border: 1px solid rgba(43, 38, 32, 0.3);
  color: var(--ink-soft);
  pointer-events: none;
}

.ticket-action.is-done {
  background: transparent;
  border: 1px solid var(--stamp-green);
  color: var(--stamp-green);
  pointer-events: none;
}

/* ─── STAMP ANIMATION ─── */

.stamp-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.stamp-mark {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 22px;
  letter-spacing: 2px;
  border: 3px solid var(--stamp-green);
  color: var(--stamp-green);
  padding: 6px 14px;
  transform: rotate(-10deg) scale(0.4);
  opacity: 0;
  animation: stampIn 0.5s ease forwards;
}

.stamp-mark.reject {
  border-color: var(--stamp-red);
  color: var(--stamp-red);
}

@keyframes stampIn {
  0% {
    transform: rotate(-10deg) scale(2.4);
    opacity: 0;
  }
  60% {
    transform: rotate(-10deg) scale(0.9);
    opacity: 1;
  }
  100% {
    transform: rotate(-10deg) scale(1);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .stamp-mark {
    animation: none;
    opacity: 1;
    transform: rotate(-10deg) scale(1);
  }
}

/* ─── MODAL ─── */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 20px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.modal-overlay.open {
  opacity: 1;
  pointer-events: all;
}

.modal {
  background: var(--panel);
  border: 1px solid var(--hairline);
  width: 100%;
  max-width: 480px;
  padding: 28px;
}

.modal h3 {
  font-family: var(--font-display);
  font-size: 18px;
  letter-spacing: 0.5px;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

/* ─── TOAST ─── */

.toast {
  position: fixed;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--panel-raised);
  border: 1px solid var(--amber);
  color: var(--text);
  padding: 11px 20px;
  font-size: 13px;
  font-family: var(--font-mono);
  border-radius: 2px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease, transform 0.25s ease;
  z-index: 100;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(-6px);
}

/* ─── LOADING STATE ─── */

.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  flex-direction: column;
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--hairline);
  border-top-color: var(--amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
}
```

### `frontend/src/firebase.js`

```javascript
/**
 * Firebase client SDK initialization.
 * Uses environment variables from .env (prefixed with VITE_ for Vite).
 */

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendEmailVerification,
  onAuthStateChanged,
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export {
  auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendEmailVerification,
  onAuthStateChanged,
};
```

### `frontend/src/utils/api.js`

```javascript
/**
 * Axios instance pre-configured with:
 * - Base URL from environment
 * - Automatic Firebase ID token injection in Authorization header
 *
 * Every API call automatically includes the current user's token,
 * so routes/components don't need to manage auth headers manually.
 */

import axios from 'axios';
import { auth } from '../firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — injects Firebase ID token
api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        console.error('Authentication error:', data.detail);
      } else if (status === 403) {
        console.error('Authorization error:', data.detail);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### `frontend/src/contexts/AuthContext.jsx`

```jsx
/**
 * Auth Context — provides Firebase auth state + user role to all components.
 *
 * On auth state change:
 * 1. If user is logged in → fetch their profile from /api/me → get role
 * 2. Provides: currentUser (Firebase user), userProfile (MongoDB doc with role),
 *    loading, login, signup, logout functions
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendEmailVerification,
  onAuthStateChanged,
} from '../firebase';
import api from '../utils/api';

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);   // Firebase user object
  const [userProfile, setUserProfile] = useState(null);    // { firebase_uid, email, name, role }
  const [loading, setLoading] = useState(true);

  // Listen for Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      if (user) {
        try {
          const res = await api.get('/api/me');
          setUserProfile(res.data);
        } catch (err) {
          // User exists in Firebase but not registered in our DB yet
          // This happens between Firebase signup and /api/register call
          setUserProfile(null);
        }
      } else {
        setUserProfile(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Sign up: create Firebase account → send verification email → register in backend
  async function signup(email, password, name, role) {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Send verification email
    await sendEmailVerification(user);

    // Register in our backend (creates MongoDB user doc with role)
    const token = await user.getIdToken();
    const res = await api.post('/api/register', {
      firebase_uid: user.uid,
      email: email,
      name: name,
      role: role,
    });

    setUserProfile(res.data);
    return user;
  }

  // Login: sign in with Firebase → fetch profile from backend
  async function login(email, password) {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    const res = await api.get('/api/me');
    setUserProfile(res.data);
    return user;
  }

  // Logout
  async function logout() {
    await signOut(auth);
    setUserProfile(null);
  }

  const value = {
    currentUser,
    userProfile,
    loading,
    signup,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

### `frontend/src/components/Toast.jsx`

```jsx
/**
 * Toast notification component.
 * Shows a brief message at the bottom of the screen.
 * Auto-hides after 2.6 seconds.
 */

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';

const ToastContext = createContext(null);

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }) {
  const [message, setMessage] = useState('');
  const [visible, setVisible] = useState(false);

  const showToast = useCallback((msg) => {
    setMessage(msg);
    setVisible(true);
  }, []);

  useEffect(() => {
    if (visible) {
      const timer = setTimeout(() => setVisible(false), 2600);
      return () => clearTimeout(timer);
    }
  }, [visible, message]);

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className={`toast ${visible ? 'show' : ''}`} role="status" aria-live="polite">
        {message}
      </div>
    </ToastContext.Provider>
  );
}
```

### `frontend/src/components/AuthScreen.jsx`

```jsx
/**
 * Auth Screen — Login ("Clock In") and Signup ("New Hire") tabs.
 * Matches the Foreman industrial aesthetic from the prototype.
 */

import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from './Toast';

export default function AuthScreen() {
  const [mode, setMode] = useState('login'); // 'login' or 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('manager');
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { signup, login } = useAuth();
  const showToast = useToast();

  function validate() {
    const errs = {};
    if (!/^\S+@\S+\.\S+$/.test(email)) errs.email = 'Enter a valid email address.';
    if (password.length < 6) errs.password = 'Password needs at least 6 characters.';
    if (mode === 'signup' && name.length < 2) errs.name = "Tell us who's clocking in.";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);

    try {
      if (mode === 'signup') {
        await signup(email, password, name, role);
        showToast('Account created — verification email sent.');
      } else {
        await login(email, password);
        showToast('Welcome back!');
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Something went wrong.';
      setErrors({ form: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-wrap">
        {/* Left side — branding */}
        <div className="auth-side">
          <div>
            <div className="brand-mark">
              <span className="rivet"></span>
              <span>Foreman</span>
            </div>
            <h1>Assign the work.<br />Inspect what's done.</h1>
            <p>
              A job board for teams who need real sign-off before work counts
              as finished — not just a checkbox.
            </p>
          </div>
          <div className="ledger">
            <div><b>01</b>&nbsp; Manager opens a work order, sets the complexity, assigns the crew.</div>
            <div><b>02</b>&nbsp; Employee does the job, then submits it for inspection.</div>
            <div><b>03</b>&nbsp; Manager confirms or sends it back — nothing is "done" until it's stamped.</div>
          </div>
        </div>

        {/* Right side — form */}
        <div className="auth-form-area">
          <div className="auth-tabs">
            <button
              className={`auth-tab ${mode === 'login' ? 'is-active' : ''}`}
              onClick={() => { setMode('login'); setErrors({}); }}
              type="button"
              id="tab-login"
            >
              Clock In
            </button>
            <button
              className={`auth-tab ${mode === 'signup' ? 'is-active' : ''}`}
              onClick={() => { setMode('signup'); setErrors({}); }}
              type="button"
              id="tab-signup"
            >
              New Hire
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {mode === 'signup' && (
              <div className={`field ${errors.name ? 'has-error' : ''}`}>
                <label htmlFor="inp-name">Full name</label>
                <input
                  id="inp-name"
                  type="text"
                  placeholder="e.g. Saad Khan"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
                {errors.name && <div className="field-error">{errors.name}</div>}
              </div>
            )}

            <div className={`field ${errors.email ? 'has-error' : ''}`}>
              <label htmlFor="inp-email">Work email</label>
              <input
                id="inp-email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              {errors.email && <div className="field-error">{errors.email}</div>}
            </div>

            <div className={`field ${errors.password ? 'has-error' : ''}`}>
              <label htmlFor="inp-password">Password</label>
              <input
                id="inp-password"
                type="password"
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {errors.password && <div className="field-error">{errors.password}</div>}
            </div>

            {mode === 'signup' && (
              <div className="field">
                <label>You are a...</label>
                <div className="role-pick">
                  <button
                    type="button"
                    className={`role-opt ${role === 'manager' ? 'is-selected' : ''}`}
                    onClick={() => setRole('manager')}
                  >
                    <b>Manager</b>
                    <small>Assigns work orders, sets complexity, signs off finished jobs.</small>
                  </button>
                  <button
                    type="button"
                    className={`role-opt ${role === 'employee' ? 'is-selected' : ''}`}
                    onClick={() => setRole('employee')}
                  >
                    <b>Employee</b>
                    <small>Views assigned jobs and submits them for inspection.</small>
                  </button>
                </div>
              </div>
            )}

            {errors.form && (
              <div className="field-error" style={{ marginBottom: 12, display: 'block' }}>
                {errors.form}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={submitting}
              id="btn-auth-submit"
            >
              {submitting
                ? 'Processing...'
                : mode === 'signup'
                  ? 'Create Account'
                  : 'Clock In'}
            </button>
          </form>

          <div className="auth-foot">
            {mode === 'signup'
              ? 'A verification email will be sent to confirm your address.'
              : "Don't have an account? Click 'New Hire' above to register."}
          </div>
        </div>
      </div>
    </div>
  );
}
```

### `frontend/src/components/Topbar.jsx`

```jsx
/**
 * Top navigation bar — brand mark, page title, user badge, logout.
 */

import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Topbar() {
  const { userProfile, logout } = useAuth();

  if (!userProfile) return null;

  const initials = userProfile.name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const isManager = userProfile.role === 'manager';
  const pageTitle = isManager ? 'Job Board — Manager View' : 'My Work Orders';

  return (
    <div className="topbar">
      <div className="brand-mark">
        <span className="rivet"></span>
        <span>Foreman</span>
      </div>
      <div className="topbar-divider"></div>
      <div className="topbar-title">{pageTitle}</div>
      <div className="topbar-spacer"></div>

      <div className={`id-badge ${isManager ? '' : 'role-employee'}`}>
        <div className="avatar">{initials}</div>
        <div className="meta">
          <b>{userProfile.name}</b>
          <small>{isManager ? 'Manager' : 'Employee'}</small>
        </div>
      </div>

      <button className="icon-btn" title="Sign out" onClick={logout}>
        ⏏
      </button>
    </div>
  );
}
```

### `frontend/src/components/TicketCard.jsx`

```jsx
/**
 * Ticket Card — paper-style task card with pin, complexity dots,
 * assignee avatar, and role-appropriate action buttons.
 * Includes stamp animation for approve/reject.
 */

import React, { useState, useRef } from 'react';

function ComplexityDots({ level }) {
  return (
    <div className="complexity-dots">
      {[1, 2, 3].map((i) => (
        <span key={i} className={i <= level ? 'filled' : 'empty'}>●</span>
      ))}
    </div>
  );
}

export default function TicketCard({ task, userRole, onStart, onSubmit }) {
  const [stamped, setStamped] = useState(null); // 'approved' or 'rejected' or null
  const cardRef = useRef(null);

  const isRework = task.is_rejected && task.stage !== 'submitted_for_review' && task.stage !== 'done';

  const assigneeName = task.assigned_to_name || 'Unknown';
  const initials = assigneeName
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  function renderAction() {
    if (userRole !== 'employee') return null;

    switch (task.stage) {
      case 'todo':
        return (
          <button className="ticket-action" onClick={() => onStart?.(task.id)}>
            Start Job
          </button>
        );
      case 'in_progress':
        return (
          <button className="ticket-action" onClick={() => onSubmit?.(task.id)}>
            {isRework ? 'Resubmit for Inspection' : 'Submit for Inspection'}
          </button>
        );
      case 'submitted_for_review':
        return (
          <button className="ticket-action is-disabled">
            Awaiting Inspection…
          </button>
        );
      case 'done':
        return (
          <button className="ticket-action is-done">
            Signed Off ✓
          </button>
        );
      default:
        return null;
    }
  }

  return (
    <div className={`ticket ${isRework ? 'is-rework' : ''}`} ref={cardRef}>
      <div className="pin"></div>
      <div className="ticket-id">{task.id?.slice(-8) || 'N/A'}</div>
      <div className="ticket-title">{task.title}</div>
      <div className="ticket-desc">{task.description}</div>

      {isRework && task.rejection_feedback && (
        <div className="rework-note">
          <b>Sent back by Manager</b>
          {task.rejection_feedback}
        </div>
      )}

      <div className="ticket-meta">
        <ComplexityDots level={task.complexity} />
        <div className="ticket-assignee">
          <div className="mini-avatar">{initials}</div>
          <span>{assigneeName.split(' ')[0]}</span>
        </div>
      </div>

      {renderAction()}

      {stamped && (
        <div className="stamp-overlay">
          <div className={`stamp-mark ${stamped === 'rejected' ? 'reject' : ''}`}>
            {stamped === 'rejected' ? 'SENT BACK' : 'APPROVED'}
          </div>
        </div>
      )}
    </div>
  );
}
```

### `frontend/src/components/BoardColumn.jsx`

```jsx
/**
 * Kanban board column — renders a list of TicketCards for a given stage.
 */

import React from 'react';
import TicketCard from './TicketCard';

const STAGE_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  submitted_for_review: 'For Inspection',
  done: 'Signed Off',
};

export default function BoardColumn({ stage, tasks, userRole, onStart, onSubmit }) {
  const label = STAGE_LABELS[stage] || stage;

  return (
    <div className="column">
      <div className="column-head">
        <h4>{label}</h4>
        <span className="n">{tasks.length}</span>
      </div>
      <div className="column-body">
        {tasks.length === 0 ? (
          <div className="column-empty">No work orders here</div>
        ) : (
          tasks.map((task) => (
            <TicketCard
              key={task.id}
              task={task}
              userRole={userRole}
              onStart={onStart}
              onSubmit={onSubmit}
            />
          ))
        )}
      </div>
    </div>
  );
}
```

### `frontend/src/components/InspectionQueue.jsx`

```jsx
/**
 * Inspection Queue — Manager's "PR inbox" for tasks awaiting review.
 * Shows confirm/reject buttons with inline reject-feedback panel.
 */

import React, { useState } from 'react';

function ComplexityDots({ level }) {
  return (
    <span className="complexity-dots" style={{ display: 'inline' }}>
      {[1, 2, 3].map((i) => (
        <span key={i} className={i <= level ? 'filled' : 'empty'}>●</span>
      ))}
    </span>
  );
}

export default function InspectionQueue({ tasks, onConfirm, onReject }) {
  const [openRejectId, setOpenRejectId] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  function handleReject(taskId) {
    const feedback = rejectReason.trim() || 'Needs another pass before it can be signed off.';
    onReject(taskId, feedback);
    setOpenRejectId(null);
    setRejectReason('');
  }

  return (
    <div className="queue-section">
      <div className="queue-section-head">
        <h3>Inspection Queue</h3>
        <span className="count-pill">{tasks.length}</span>
      </div>
      <div className="queue-list">
        {tasks.length === 0 ? (
          <div className="empty-queue">Nothing waiting on inspection right now.</div>
        ) : (
          tasks.map((task) => (
            <div className="queue-item" key={task.id}>
              <div className="qi-main">
                <div className="qi-title">{task.title}</div>
                <div className="qi-sub">
                  {task.id?.slice(-8)} · Submitted by {task.assigned_to_name || 'Unknown'} ·{' '}
                  Complexity <ComplexityDots level={task.complexity} />
                </div>
              </div>
              <div className="queue-actions">
                <button
                  className="btn btn-sm btn-stamp-approve"
                  onClick={() => onConfirm(task.id)}
                >
                  Confirm
                </button>
                <button
                  className="btn btn-sm btn-stamp-reject"
                  onClick={() =>
                    setOpenRejectId(openRejectId === task.id ? null : task.id)
                  }
                >
                  Send Back
                </button>
              </div>
              {openRejectId === task.id && (
                <div className="reject-panel">
                  <textarea
                    placeholder="What needs to be fixed before this can be signed off?"
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                  />
                  <div className="reject-actions">
                    <button
                      className="btn btn-sm btn-stamp-reject"
                      onClick={() => handleReject(task.id)}
                    >
                      Confirm rejection
                    </button>
                    <button
                      className="btn btn-sm btn-ghost"
                      onClick={() => {
                        setOpenRejectId(null);
                        setRejectReason('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

### `frontend/src/components/NewTaskModal.jsx`

```jsx
/**
 * New Work Order modal — Manager creates and assigns tasks.
 */

import React, { useState, useEffect } from 'react';
import api from '../utils/api';

export default function NewTaskModal({ isOpen, onClose, onCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [assignee, setAssignee] = useState('');
  const [complexity, setComplexity] = useState(2);
  const [employees, setEmployees] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.get('/api/users/employees').then((res) => {
        setEmployees(res.data);
        if (res.data.length > 0) setAssignee(res.data[0].firebase_uid);
      });
    }
  }, [isOpen]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);

    try {
      await api.post('/api/tasks', {
        title: title.trim(),
        description: description.trim() || 'No description provided.',
        assigned_to: assignee,
        complexity: parseInt(complexity, 10),
      });
      setTitle('');
      setDescription('');
      setComplexity(2);
      onCreated?.();
      onClose();
    } catch (err) {
      console.error('Failed to create task:', err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={`modal-overlay ${isOpen ? 'open' : ''}`} onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>New work order</h3>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="nt-title">Title</label>
            <input
              id="nt-title"
              type="text"
              placeholder="e.g. Fix Nginx upstream config"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="nt-desc">Description</label>
            <input
              id="nt-desc"
              type="text"
              placeholder="What needs to happen"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="nt-assignee">Assign to</label>
            <select
              id="nt-assignee"
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
            >
              {employees.map((emp) => (
                <option key={emp.firebase_uid} value={emp.firebase_uid}>
                  {emp.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="nt-complexity">Complexity</label>
            <select
              id="nt-complexity"
              value={complexity}
              onChange={(e) => setComplexity(e.target.value)}
            >
              <option value={1}>Low</option>
              <option value={2}>Medium</option>
              <option value={3}>High</option>
            </select>
          </div>
          <div className="modal-actions">
            <button
              type="submit"
              className="btn btn-primary"
              style={{ flex: 1 }}
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Open work order'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

### `frontend/src/components/RejectPanel.jsx`

```jsx
/**
 * Reject Panel — inline feedback form for rejecting a task submission.
 * Extracted as a reusable component.
 */

import React, { useState } from 'react';

export default function RejectPanel({ taskId, onReject, onCancel }) {
  const [reason, setReason] = useState('');

  function handleSubmit() {
    const feedback = reason.trim() || 'Needs another pass before it can be signed off.';
    onReject(taskId, feedback);
    setReason('');
  }

  return (
    <div className="reject-panel">
      <textarea
        placeholder="What needs to be fixed before this can be signed off?"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
      />
      <div className="reject-actions">
        <button className="btn btn-sm btn-stamp-reject" onClick={handleSubmit}>
          Confirm rejection
        </button>
        <button className="btn btn-sm btn-ghost" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}
```

### `frontend/src/pages/ManagerDashboard.jsx`

```jsx
/**
 * Manager Dashboard — full board + inspection queue + "New Work Order" button.
 * Manager sees ALL tasks across all employees.
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import BoardColumn from '../components/BoardColumn';
import InspectionQueue from '../components/InspectionQueue';
import NewTaskModal from '../components/NewTaskModal';
import { useToast } from '../components/Toast';

const STAGES = ['todo', 'in_progress', 'submitted_for_review', 'done'];

export default function ManagerDashboard() {
  const [tasks, setTasks] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const showToast = useToast();

  const fetchTasks = useCallback(async () => {
    try {
      const res = await api.get('/api/tasks');
      setTasks(res.data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const pendingInspection = tasks.filter((t) => t.stage === 'submitted_for_review');

  async function handleConfirm(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/review`, {
        action: 'confirm',
      });
      showToast('Task signed off and marked Done.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to confirm task.');
    }
  }

  async function handleReject(taskId, feedback) {
    try {
      await api.post(`/api/tasks/${taskId}/review`, {
        action: 'reject',
        feedback,
      });
      showToast('Task sent back for revision.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to reject task.');
    }
  }

  if (loading) {
    return (
      <div className="content">
        <div className="loading-screen" style={{ minHeight: '50vh' }}>
          <div className="spinner"></div>
          <div className="loading-text">Loading work orders…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <h2>Job Board</h2>
          <p>Open new work orders, assign the crew, and inspect what comes back.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
          + New Work Order
        </button>
      </div>

      <InspectionQueue
        tasks={pendingInspection}
        onConfirm={handleConfirm}
        onReject={handleReject}
      />

      <div className="board">
        {STAGES.map((stage) => (
          <BoardColumn
            key={stage}
            stage={stage}
            tasks={tasks.filter((t) => t.stage === stage)}
            userRole="manager"
          />
        ))}
      </div>

      <NewTaskModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={fetchTasks}
      />
    </div>
  );
}
```

### `frontend/src/pages/EmployeeDashboard.jsx`

```jsx
/**
 * Employee Dashboard — filtered board (own tasks only) + submit actions.
 * Employee can: start jobs, submit for inspection.
 * Employee CANNOT: create tasks, confirm/reject, see other employees' tasks.
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import BoardColumn from '../components/BoardColumn';
import { useToast } from '../components/Toast';

const STAGES = ['todo', 'in_progress', 'submitted_for_review', 'done'];

export default function EmployeeDashboard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const showToast = useToast();

  const fetchTasks = useCallback(async () => {
    try {
      const res = await api.get('/api/tasks');
      setTasks(res.data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  async function handleStart(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/start`);
      showToast('Job started — moved to In Progress.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to start task.');
    }
  }

  async function handleSubmit(taskId) {
    try {
      await api.post(`/api/tasks/${taskId}/submit`);
      showToast('Submitted for inspection — awaiting manager review.');
      fetchTasks();
    } catch (err) {
      showToast('Failed to submit task.');
    }
  }

  if (loading) {
    return (
      <div className="content">
        <div className="loading-screen" style={{ minHeight: '50vh' }}>
          <div className="spinner"></div>
          <div className="loading-text">Loading your work orders…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <h2>My Work Orders</h2>
          <p>
            Jobs assigned to you. Submit finished work for inspection — your Manager
            signs off before it counts as done.
          </p>
        </div>
      </div>

      <div className="board">
        {STAGES.map((stage) => (
          <BoardColumn
            key={stage}
            stage={stage}
            tasks={tasks.filter((t) => t.stage === stage)}
            userRole="employee"
            onStart={handleStart}
            onSubmit={handleSubmit}
          />
        ))}
      </div>
    </div>
  );
}
```

### `frontend/src/App.jsx`

```jsx
/**
 * Root application component.
 * Handles role-based routing:
 * - Not logged in → AuthScreen
 * - Logged in as Manager → ManagerDashboard
 * - Logged in as Employee → EmployeeDashboard
 */

import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import AuthScreen from './components/AuthScreen';
import Topbar from './components/Topbar';
import ManagerDashboard from './pages/ManagerDashboard';
import EmployeeDashboard from './pages/EmployeeDashboard';

function AppContent() {
  const { currentUser, userProfile, loading } = useAuth();

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <div className="loading-text">Initializing…</div>
      </div>
    );
  }

  // Not logged in or not registered → show auth screen
  if (!currentUser || !userProfile) {
    return <AuthScreen />;
  }

  // Logged in — render role-appropriate dashboard
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Topbar />
      {userProfile.role === 'manager' ? <ManagerDashboard /> : <EmployeeDashboard />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}
```

---

## 1.5 — Running the MVP Locally (Before Any Docker)

### Backend

```bash
cd backend

# Create Python virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env with your real values
cp .env.example .env
# Edit .env with your actual MONGO_URI and FIREBASE_SERVICE_ACCOUNT_PATH

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
✔ Connected to MongoDB: foreman_db
INFO:     Application startup complete.
```

**Verify:** Open `http://localhost:8000/api/health` in your browser. Expected response:

```json
{"status": "healthy", "service": "foreman-backend"}
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env with your real values
cp .env.example .env
# Edit .env with your actual Firebase config values

# Run the dev server
npm run dev
```

**Expected output:**

```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

**Verify:** Open `http://localhost:5173` in your browser. You should see the Foreman auth screen with the "Clock In" / "New Hire" tabs.

### End-to-End Test (Manual)

1. Open `http://localhost:5173`
2. Click **"New Hire"** tab → Enter name, email, password → Select **Manager** → Click **Create Account**
3. Check your email for Firebase verification link (optional — app works without it for now)
4. You should land on the **Manager Dashboard** with an empty board
5. Open a new incognito/private window → Go to `http://localhost:5173`
6. Click **"New Hire"** → Create an **Employee** account with a different email
7. Back in the Manager window → Click **"+ New Work Order"** → Assign a task to the employee
8. In the Employee window → Refresh → You should see the task in "To Do"
9. Click **"Start Job"** → Task moves to "In Progress"
10. Click **"Submit for Inspection"** → Task moves to "For Inspection"
11. Back in Manager window → Refresh → Task appears in the **Inspection Queue**
12. Click **"Confirm"** → Task moves to "Signed Off" / Done ✓
13. Or click **"Send Back"** → Enter feedback → Task goes back to employee's "In Progress" with rejection note

**This completes the core PR-review-merge workflow.**

---

## 1.6 — Ismail Pushes Starter Code

```bash
# From repo root
git add -A
git commit -m "feat: complete MVP — FastAPI backend + React frontend with Firebase auth and role-based task approval workflow"
git push origin develop

# Create PR from develop → main
# Ismail reviews and merges his own initial commit (bootstrapping exception)
# Then Ibrahim and Saad clone:
```

**Ibrahim and Saad run:**

```bash
git clone https://github.com/<your-org>/foreman-kanban.git
cd foreman-kanban
```

> Ismail shares `.env` files and `serviceAccountKey.json` securely (encrypted zip/private DM). Each teammate places them in their correct directories.

---

# PHASE 2 — Architecture Design

## 2.1 — Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              BROWSER (End User)                                  │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                       React SPA (Vite Build)                                │  │
│  │                                                                             │  │
│  │  AuthScreen ──▶ Firebase Auth SDK ──▶ Firebase Auth Service (Google Cloud)  │  │
│  │       │                                       │                             │  │
│  │       │ (gets ID token)                       │ (creates account,           │  │
│  │       ▼                                       │  sends verification email)  │  │
│  │  AuthContext (stores token + role)                                          │  │
│  │       │                                                                     │  │
│  │       ▼                                                                     │  │
│  │  API calls with Authorization: Bearer <firebase_id_token>                  │  │
│  │       │                                                                     │  │
│  │  ManagerDashboard  ◀──▶  EmployeeDashboard                                │  │
│  │  (CRUD + review)         (view + submit)                                   │  │
│  └──────┬──────────────────────────────────────────────────────────────────────┘  │
│         │                                                                        │
└─────────┼────────────────────────────────────────────────────────────────────────┘
          │ HTTP (REST API)
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          NGINX (Reverse Proxy)                                   │
│                                                                                  │
│  Static files (React build) ──▶ served directly                                │
│  /api/* requests             ──▶ proxied to FastAPI                             │
└─────────┬────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend (Python)                                  │
│                                                                                  │
│  ┌───────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐   │
│  │ Firebase Admin SDK │   │ Role Guard Middleware │   │ Status Machine       │   │
│  │                   │   │                      │   │                      │   │
│  │ verify_id_token() │──▶│ require_role("mgr")  │──▶│ validate_transition()│   │
│  │                   │   │ require_role("emp")  │   │                      │   │
│  │ UID ──▶ user doc  │   │ 401 / 403 on fail    │   │ legal stage changes  │   │
│  └───────────────────┘   └──────────────────────┘   └──────────────────────┘   │
│         │                                                                       │
│         ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                          Route Handlers                                 │    │
│  │  POST /api/register          GET  /api/tasks                           │    │
│  │  GET  /api/me                POST /api/tasks                           │    │
│  │  GET  /api/users/employees   POST /api/tasks/{id}/start                │    │
│  │                              POST /api/tasks/{id}/submit               │    │
│  │                              POST /api/tasks/{id}/review               │    │
│  │                              PUT  /api/tasks/{id}                      │    │
│  │                              DELETE /api/tasks/{id}                    │    │
│  └──────────────────────────────────┬──────────────────────────────────────┘    │
│                                     │                                           │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                      │ MongoDB Driver (motor)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MongoDB (Atlas Free M0)                                  │
│                                                                                  │
│  Database: foreman_db                                                           │
│                                                                                  │
│  Collection: users                     Collection: tasks                        │
│  ┌──────────────────────────────┐     ┌──────────────────────────────────┐      │
│  │ { firebase_uid, email,       │     │ { title, description,            │      │
│  │   name, role }               │     │   assigned_to, complexity,       │      │
│  └──────────────────────────────┘     │   stage, is_rejected,            │      │
│                                       │   rejection_feedback,            │      │
│                                       │   created_by, created_at,        │      │
│                                       │   updated_at }                   │      │
│                                       └──────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 — Task Approval State Machine (PR Review/Merge Analog)

```
                 ┌──────────────────────────────────────────────────────┐
                 │           TASK STATUS STATE MACHINE                    │
                 │         (Mirrors PR Review/Merge Flow)                │
                 └──────────────────────────────────────────────────────┘

                          Employee action          Employee action
                 ┌─────┐  "Start Job"    ┌────────────┐  "Submit"    ┌─────────────────────┐
                 │ TODO │───────────────▶│ IN PROGRESS │────────────▶│ SUBMITTED FOR REVIEW │
                 └─────┘                 └────────────┘              └──────────┬────────────┘
                                               ▲                               │
                                               │                    ┌──────────┴──────────┐
                                               │                    │                     │
                                               │          Manager action:          Manager action:
                                               │          "Reject"                 "Confirm"
                                               │          (+ feedback)             (= Merge)
                                               │                    │                     │
                                               │                    ▼                     ▼
                                               │            ┌──────────────┐       ┌──────┐
                                               └────────────│  REJECTED /  │       │ DONE │
                                                            │  IN PROGRESS │       │  ✓   │
                                                            │  (+ feedback)│       └──────┘
                                                            └──────────────┘     (Terminal)

  Analogy:
  ┌────────────────────────┬──────────────────────────────────────┐
  │ Foreman Task Flow      │ GitHub Pull Request Flow             │
  ├────────────────────────┼──────────────────────────────────────┤
  │ Employee starts job    │ Developer creates feature branch     │
  │ Employee submits       │ Developer opens Pull Request         │
  │ Manager inspects       │ Reviewer reviews the PR              │
  │ Manager confirms       │ Reviewer approves + merges           │
  │ Manager rejects        │ Reviewer requests changes            │
  │ Employee reworks       │ Developer pushes new commits         │
  │ Employee resubmits     │ Developer re-requests review         │
  └────────────────────────┴──────────────────────────────────────┘
```

## 2.3 — Docker Architecture

```
┌─────────────────────────── docker-compose.yml ──────────────────────────┐
│                                                                         │
│  Network: foreman-net (bridge)                                         │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  │
│  │  frontend        │  │  backend             │  │  mongo            │  │
│  │                  │  │                      │  │                   │  │
│  │  Image:          │  │  Image:              │  │  Image:           │  │
│  │  foreman-        │  │  foreman-backend     │  │  mongo:7          │  │
│  │  frontend        │  │                      │  │                   │  │
│  │                  │  │  Port: 8000          │  │  Port: 27017      │  │
│  │  Port: 80→80     │  │                      │  │  (internal)       │  │
│  │  (Nginx)         │  │  Env:                │  │                   │  │
│  │                  │  │  - MONGO_URI          │  │  Volume:          │  │
│  │  Depends: backend│  │  - FIREBASE_SA_PATH   │  │  mongo-data       │  │
│  │                  │  │                      │  │  (named volume)   │  │
│  │  Health: curl    │  │  Depends: mongo       │  │                   │  │
│  │  localhost:80     │  │                      │  │  Health:          │  │
│  │                  │  │  Health: curl         │  │  mongosh --eval   │  │
│  │                  │  │  localhost:8000       │  │  "db.runCommand(  │  │
│  │                  │  │  /api/health          │  │   {ping:1})"     │  │
│  └─────────────────┘  └─────────────────────┘  └───────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.4 — Local Kubernetes Architecture

```
┌─────────────────── minikube cluster (foreman namespace) ──────────────────┐
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │                        INGRESS CONTROLLER                             ││
│  │                    foreman.local → routing rules                      ││
│  │                                                                       ││
│  │     /           → frontend-svc:80                                    ││
│  │     /api/*      → backend-svc:8000                                   ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                           │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐│
│  │ Deployment:           │  │ Deployment:           │  │ Deployment:     ││
│  │ frontend              │  │ backend               │  │ mongo           ││
│  │ replicas: 2           │  │ replicas: 2           │  │ replicas: 1     ││
│  │                      │  │                      │  │                 ││
│  │ Container:           │  │ Container:           │  │ Container:      ││
│  │ foreman-frontend     │  │ foreman-backend      │  │ mongo:7         ││
│  │                      │  │                      │  │                 ││
│  │ Service:             │  │ Service:             │  │ Service:        ││
│  │ frontend-svc         │  │ backend-svc          │  │ mongo-svc       ││
│  │ ClusterIP:80         │  │ ClusterIP:8000       │  │ ClusterIP:27017 ││
│  │                      │  │                      │  │                 ││
│  │ Probes:              │  │ Probes:              │  │ Volume:         ││
│  │ readiness: /         │  │ readiness:           │  │ PVC →           ││
│  │ liveness: /          │  │ /api/health          │  │ mongo-pvc       ││
│  │                      │  │ liveness:            │  │                 ││
│  │ ConfigMap:           │  │ /api/health          │  │                 ││
│  │ foreman-config       │  │                      │  │                 ││
│  │                      │  │ Secret:              │  │                 ││
│  │                      │  │ foreman-secrets      │  │                 ││
│  └──────────────────────┘  └──────────────────────┘  └─────────────────┘│
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  ConfigMap: foreman-config       Secret: foreman-secrets           │  │
│  │  - FRONTEND_URL                  - MONGO_URI (base64)              │  │
│  │  - API_URL                       - serviceAccountKey.json (base64) │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## 2.5 — CI/CD Pipeline Flow

```
┌────────────────── GitHub Actions ──────────────────┐
│                                                     │
│  ┌─── ON PULL REQUEST (ci.yml) ──────────────────┐ │
│  │                                                │ │
│  │  1. Checkout code                             │ │
│  │  2. Setup Python 3.12 + Node 20              │ │
│  │  3. Install backend deps (pip)                │ │
│  │  4. Install frontend deps (npm)               │ │
│  │  5. Lint backend (flake8/ruff)                │ │
│  │  6. Lint frontend (eslint)                    │ │
│  │  7. Run backend tests (pytest)                │ │
│  │  8. Build frontend (npm run build)            │ │
│  │  9. Build Docker images (no push)             │ │
│  │                                                │ │
│  │  ✓ All pass → PR is mergeable                 │ │
│  │  ✗ Any fail → PR blocked                      │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── ON MERGE TO MAIN (cd.yml) ─────────────────┐ │
│  │                                                │ │
│  │  1. Checkout code                             │ │
│  │  2. Build Docker images                       │ │
│  │  3. Push to DockerHub                         │ │
│  │     - <user>/foreman-backend:latest           │ │
│  │     - <user>/foreman-frontend:latest          │ │
│  │  4. Deploy frontend to Vercel                 │ │
│  │     (via Vercel CLI or webhook)               │ │
│  │  5. Deploy backend to Render                  │ │
│  │     (via deploy hook URL)                     │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 2.6 — Git Branching Model

```
main ─────────●─────────────────●─────────────────────●──────── (production releases)
              │                 ▲                     ▲
              │                 │ merge               │ merge
              ▼                 │                     │
develop ──────●───●───●───●─────●───●───●─────────────●──────── (integration)
                  │   │   ▲         │   ▲             ▲
                  │   │   │ merge   │   │ merge       │ merge
                  │   │   │         │   │             │
                  │   │   │         │   │      feature/devops/ci-pipeline
                  │   │   │         │   │             │
                  │   │   │         │   │             ●───●───● (Ismail)
                  │   │   │         │   │
                  │   │   │         │   │
                  │   │   │  feature/frontend/auth-screen
                  │   │   │         │
                  │   │   │         ●───●───● (Saad)
                  │   │   │
                  │   │   │
           feature/backend/task-crud
                  │
                  ●───●───● (Ibrahim)

  Branch naming convention:
  ─────────────────────────
  feature/backend/<name>     ← Ibrahim
  feature/frontend/<name>    ← Saad
  feature/devops/<name>      ← Ismail
```

## 2.7 — Cloud Deployment Architecture

```
┌──────────── FREE CLOUD DEPLOYMENT ────────────┐
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │          VERCEL (Free Tier)              │   │
│  │                                         │   │
│  │  Frontend: foreman-kanban.vercel.app    │   │
│  │  - Auto-deploy on push to main          │   │
│  │  - Environment vars for Firebase config │   │
│  │  - SPA routing via vercel.json rewrites │   │
│  └────────────────┬────────────────────────┘   │
│                   │ API calls                   │
│                   ▼                             │
│  ┌─────────────────────────────────────────┐   │
│  │          RENDER (Free Tier)              │   │
│  │                                         │   │
│  │  Backend: foreman-api.onrender.com      │   │
│  │  - Docker deploy (or native Python)     │   │
│  │  - Env vars: MONGO_URI, Firebase SA     │   │
│  │  - ⚠️ Cold starts after 15min idle      │   │
│  │  - Deploy hook for GitHub Actions CD    │   │
│  └────────────────┬────────────────────────┘   │
│                   │ MongoDB driver              │
│                   ▼                             │
│  ┌─────────────────────────────────────────┐   │
│  │       MONGODB ATLAS (M0 Free)           │   │
│  │                                         │   │
│  │  Cluster: foreman-cluster               │   │
│  │  Database: foreman_db                   │   │
│  │  - 512 MB storage                       │   │
│  │  - Shared RAM/vCPU                      │   │
│  │  - No auto-scaling (learning caveat)    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │       FIREBASE (Spark/Free Plan)        │   │
│  │                                         │   │
│  │  Auth: Email/Password provider          │   │
│  │  - Unlimited auth users (free)          │   │
│  │  - Email verification                   │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

# PHASE 3 — Git Workflow (Strict)

## 3.1 — Branch Strategy

| Branch | Purpose | Who Can Push | Who Can Merge |
|--------|---------|-------------|---------------|
| `main` | Production-ready releases | Nobody directly (protected) | **Ismail only** (via PR from `develop`) |
| `develop` | Integration branch | Nobody directly (protected) | **Ismail only** (via PR from feature branches) |
| `feature/backend/*` | Ibrahim's backend features | Ibrahim | Ismail (reviews & merges to `develop`) |
| `feature/frontend/*` | Saad's frontend features | Saad | Ismail (reviews & merges to `develop`) |
| `feature/devops/*` | Ismail's DevOps features | Ismail | Ismail (reviews his own → merges to `develop`) |

## 3.2 — Branch Protection Rules (Ismail Sets Up)

On GitHub → Repository → Settings → Branches → Add rule:

### For `main`:
- **Branch name pattern:** `main`
- ✅ Require a pull request before merging
- ✅ Require approvals: **1**
- ✅ Require status checks to pass before merging → select `ci` workflow
- ✅ Require branches to be up to date before merging
- ✅ Do not allow bypassing the above settings (even for admins)

### For `develop`:
- **Branch name pattern:** `develop`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging → select `ci` workflow

## 3.3 — PR Template

### `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Summary
<!-- What does this PR do? -->

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] DevOps / Infrastructure
- [ ] Documentation

## Changes
<!-- List the files changed and what was modified -->

## Testing
<!-- How did you test this? Include commands, screenshots, or expected output -->

## Checklist
- [ ] Code follows project style guidelines
- [ ] All existing tests pass (`pytest` / `npm test`)
- [ ] New tests added for new functionality
- [ ] Docker image builds successfully
- [ ] No secrets or `.env` values committed
- [ ] README updated if needed
```

## 3.4 — Full Git Command Sequence (Per Feature)

### Ibrahim — Example Feature: Backend Task CRUD

```bash
# 1. Start from latest develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/backend/rejection-history

# 3. Do work... edit files, test locally
# (Ibrahim builds, runs, and tests his own Docker container here)

# 4. Stage and commit
git add -A
git commit -m "feat(backend): add rejection history with comment tracking

- Added revision_history array to task model
- Track each rejection with timestamp, feedback, and rejection count
- Added GET /api/tasks/{id}/history endpoint
- Unit tests for revision tracking"

# 5. Push to GitHub
git push origin feature/backend/rejection-history

# 6. Open PR on GitHub (browser)
# Title: feat(backend): Rejection history with comment tracking
# Base: develop ← Compare: feature/backend/rejection-history
# Fill in PR template
# Request review from Ismail

# 7. If CI fails → fix locally, commit, push again
git add -A
git commit -m "fix: resolve failing test in rejection history"
git push origin feature/backend/rejection-history

# 8. Ismail reviews → requests changes → Ibrahim fixes:
git add -A
git commit -m "fix: address PR review feedback — validate feedback length"
git push origin feature/backend/rejection-history

# 9. Ismail approves and merges (ONLY Ismail clicks the merge button)

# 10. Ibrahim updates local develop
git checkout develop
git pull origin develop
# Delete the feature branch
git branch -d feature/backend/rejection-history
```

---

# PHASE 4 — Local Dev Environment Setup (All Members)

## 4.1 — Prerequisites

| Tool | Version | Install Command / Link |
|------|---------|----------------------|
| **Git** | 2.40+ | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Python** | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 20 LTS | [nodejs.org](https://nodejs.org/) |
| **Docker Desktop** | Latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **kubectl** | Latest | `choco install kubernetes-cli` (Windows) or `brew install kubectl` (Mac) |
| **minikube** | Latest | `choco install minikube` (Windows) or `brew install minikube` (Mac) |

## 4.2 — Clone & Setup (All Three Members Run This)

```bash
# Clone the repository
git clone https://github.com/<your-org>/foreman-kanban.git
cd foreman-kanban

# ─── Backend Setup ───
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

# Place .env and serviceAccountKey.json (received from Ismail)
# Verify:
python -c "from app.config import MONGO_URI; print('MONGO_URI loaded:', MONGO_URI[:20] + '...')"
# Expected: MONGO_URI loaded: mongodb+srv://forem...

# Run backend
uvicorn app.main:app --reload --port 8000
# Expected: ✔ Connected to MongoDB: foreman_db

# ─── Frontend Setup (new terminal) ───
cd ../frontend
npm install

# Place .env (received from Ismail)
# Verify:
node -e "console.log('Firebase project:', process.env.VITE_FIREBASE_PROJECT_ID || 'NOT SET — check .env')"

# Run frontend
npm run dev
# Expected: Local: http://localhost:5173/
```

## 4.3 — Troubleshooting Table

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Running uvicorn from wrong directory | Run from `backend/` directory, not `backend/app/` |
| `firebase_admin.exceptions.NotFoundError` | Wrong path to serviceAccountKey.json | Check `FIREBASE_SERVICE_ACCOUNT_PATH` in `.env` — relative to where you run uvicorn |
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB Atlas not reachable | Check Network Access in Atlas — add your IP or use `0.0.0.0/0` |
| `CORS error` in browser console | Frontend URL not in allowed origins | Check `FRONTEND_URL` in backend `.env` — must match exactly |
| `401 Unauthorized` on every API call | Firebase config mismatch | Ensure frontend `.env` Firebase config matches the same project as `serviceAccountKey.json` |
| `npm: command not found` | Node.js not installed or not in PATH | Reinstall Node.js, ensure "Add to PATH" is checked |
| Port 8000 already in use | Another process on that port | `netstat -ano | findstr 8000` → kill the process, or use `--port 8001` |
| `ENOSPC: System limit for file watchers reached` | Linux inotify limit | `echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf` |

---

# PHASE 5 — Individual DevOps Responsibility Model

> [!IMPORTANT]
> **Every team member** does all of the following independently — Docker builds, container runs, K8s deploys, CI triggers. The only difference is *which service* they own and *who merges* (always Ismail).

## 5.1 — Ibrahim (Backend DevOps)

### Build Backend Docker Image

```bash
cd backend

# Build the image (uses backend/Dockerfile)
docker build -t foreman-backend:dev .

# Expected output (last lines):
# => exporting to image
# => => naming to docker.io/library/foreman-backend:dev
```

### Run Backend Container Standalone

```bash
# Run with local MongoDB (if using local Mongo container)
docker run -d \
  --name foreman-backend \
  -p 8000:8000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/foreman_db" \
  -e FIREBASE_SERVICE_ACCOUNT_PATH="/app/serviceAccountKey.json" \
  -v $(pwd)/serviceAccountKey.json:/app/serviceAccountKey.json:ro \
  foreman-backend:dev

# Check it's running
docker ps
# Expected: foreman-backend   Up X seconds   0.0.0.0:8000->8000/tcp

# Check logs
docker logs foreman-backend
# Expected: ✔ Connected to MongoDB: foreman_db

# Test health endpoint
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","service":"foreman-backend"}
```

### Deliberately Break & Fix (Ibrahim's Troubleshooting Exercise)

**Break it:** Remove the `MONGO_URI` env var:

```bash
docker stop foreman-backend && docker rm foreman-backend
docker run -d --name foreman-backend -p 8000:8000 foreman-backend:dev

# Check logs:
docker logs foreman-backend
# Expected ERROR: ServerSelectionTimeoutError — can't connect to MongoDB
```

**Diagnose:**
```bash
# Exec into the container to inspect
docker exec -it foreman-backend sh
env | grep MONGO    # Empty — no MONGO_URI set
exit
```

**Fix:** Re-run with the correct env var (as shown above).

### Run Full Stack via Docker Compose

```bash
cd ..  # Back to repo root
docker compose up --build
# Expected: All three services start (mongo, backend, frontend)
# backend: ✔ Connected to MongoDB: foreman_db
# frontend: Nginx listening on port 80
```

### Test Both Roles (Manager + Employee)

```bash
# Register a manager
curl -X POST http://localhost:8000/api/register \
  -H "Authorization: Bearer <MANAGER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid":"uid-mgr","email":"mgr@test.com","name":"Test Manager","role":"manager"}'

# Register an employee
curl -X POST http://localhost:8000/api/register \
  -H "Authorization: Bearer <EMPLOYEE_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid":"uid-emp","email":"emp@test.com","name":"Test Employee","role":"employee"}'

# Create task as manager
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <MANAGER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","assigned_to":"uid-emp","complexity":2}'

# Try creating task as employee (should fail 403)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <EMPLOYEE_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Sneaky Task","assigned_to":"uid-emp","complexity":1}'
# Expected: 403 {"detail":"Access denied. This endpoint requires the 'manager' role."}
```

## 5.2 — Saad (Frontend DevOps)

### Build Frontend Docker Image

```bash
cd frontend

# Build the image (uses frontend/Dockerfile — multi-stage with Nginx)
docker build -t foreman-frontend:dev .

# Expected output:
# => exporting to image
# => => naming to docker.io/library/foreman-frontend:dev
```

### Run Frontend Container Standalone

```bash
docker run -d \
  --name foreman-frontend \
  -p 3000:80 \
  foreman-frontend:dev

# Check it's running
docker ps
# Expected: foreman-frontend   Up X seconds   0.0.0.0:3000->80/tcp

# Test in browser
# Open http://localhost:3000 — should see the Foreman auth screen
```

### Deliberately Break & Fix (Saad's Troubleshooting Exercise)

**Break it:** Modify `nginx.conf` to proxy `/api` to the wrong port:

```bash
# Edit nginx.conf — change proxy_pass to port 9999 (nothing running there)
# Rebuild and run
docker build -t foreman-frontend:broken .
docker run -d --name foreman-frontend-broken -p 3001:80 foreman-frontend:broken
```

**Diagnose:**
```bash
# Open http://localhost:3001 — auth screen loads (static files work)
# Try to log in — API calls fail with 502 Bad Gateway
docker logs foreman-frontend-broken
# Expected: connect() failed (111: Connection refused) upstream: "http://localhost:9999..."
```

**Fix:** Correct the `proxy_pass` URL in `nginx.conf`, rebuild, and redeploy.

### Test Both Roles via UI

1. Open `http://localhost:3000`
2. Create a Manager account → Verify: sees "Job Board" heading, "New Work Order" button, Inspection Queue
3. Create an Employee account (incognito window) → Verify: sees "My Work Orders" heading, no create button
4. As Manager: create a task assigned to the employee
5. As Employee: start the task → submit for inspection
6. As Manager: confirm or reject → verify the stamp animation works

## 5.3 — Ismail (Full Stack DevOps — Integration)

### Build Both Images & Run Full Stack

```bash
# From repo root
docker compose build
docker compose up -d

# Verify all services
docker compose ps
# Expected:
# foreman-backend    Up (healthy)   0.0.0.0:8000->8000/tcp
# foreman-frontend   Up (healthy)   0.0.0.0:80->80/tcp
# foreman-mongo      Up (healthy)   27017/tcp

# Check health
curl http://localhost:8000/api/health
curl http://localhost:80
```

### Deploy to Local Kubernetes

```bash
# Start minikube
minikube start

# Apply all K8s manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/mongo-pv.yml
kubectl apply -f k8s/mongo-deployment.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/ingress.yml

# Verify
kubectl get all -n foreman
```

### Deliberately Break & Fix (Ismail's Troubleshooting Exercise)

**Break it:** Set the wrong Docker image tag in `backend-deployment.yml`:

```yaml
image: foreman-backend:nonexistent-tag
```

**Diagnose:**
```bash
kubectl apply -f k8s/backend-deployment.yml
kubectl get pods -n foreman
# Expected: ErrImagePull or ImagePullBackOff

kubectl describe pod <pod-name> -n foreman
# Events section shows: "Failed to pull image... not found"
```

**Fix:** Correct the image tag, re-apply, verify pods are Running.

---

# PHASE 6 — Feature Increments (5 Per Person — Large, Substantial Features)

> [!IMPORTANT]
> Each feature below is a **genuinely large capability** spanning multiple files. For each feature, we provide: name, rationale, given starter/partial code, exact remaining task, exact files, branch name, PR title, and git commands. Only the **explicitly marked sections** are left for the student to implement — everything else is provided in full.

---

## 6.1 — Ibrahim (Backend) — 5 Features

### Feature B1: Rejection History with Comment Tracking

**Why it's substantial:** Currently, when a manager rejects a task, the old feedback is overwritten. This feature adds a full revision history — every rejection is tracked with timestamp, feedback, and count. This is like viewing a PR's review history.

**Branch:** `feature/backend/rejection-history`
**PR Title:** `feat(backend): Rejection history with revision tracking`
**Files touched:** `backend/app/models/task.py`, `backend/app/routes/task_routes.py`, `backend/tests/test_tasks.py`

**Given starter code** — add to `backend/app/models/task.py`:

```python
class RevisionEntry(BaseModel):
    """A single rejection/revision record."""
    revision_number: int
    rejected_at: datetime
    feedback: str
    rejected_by: str  # Firebase UID of the manager who rejected


class TaskResponse(BaseModel):
    # ... existing fields ...
    revision_history: list[RevisionEntry] = []
    revision_count: int = 0
```

**Ibrahim's task:** Modify the `review_task` endpoint in `task_routes.py` so that when `action='reject'`:
1. Append a new `RevisionEntry` to the task's `revision_history` array in MongoDB (use `$push`)
2. Increment `revision_count` (use `$inc`)
3. Add a new endpoint `GET /api/tasks/{task_id}/history` that returns the revision history for a task

**Expected behavior:**
- `POST /api/tasks/{id}/review` with `action=reject` → appends to history, returns updated task with `revision_count` incremented
- `GET /api/tasks/{id}/history` → returns `{"task_id": "...", "revision_count": 2, "revisions": [...]}`
- Employee resubmits → manager rejects again → history now has 2 entries
- 404 if task doesn't exist, 403 if non-manager calls history endpoint

**Git commands:**
```bash
git checkout develop && git pull origin develop
git checkout -b feature/backend/rejection-history
# ... implement ...
git add -A
git commit -m "feat(backend): add rejection history with revision tracking"
git push origin feature/backend/rejection-history
# Open PR → Ismail reviews → merges
```

---

### Feature B2: Task Complexity-Weighted Workload Dashboard

**Why it's substantial:** A new analytics endpoint that calculates each employee's workload — number of tasks weighted by complexity, broken down by stage. Managers use this to make fair assignments.

**Branch:** `feature/backend/workload-dashboard`
**PR Title:** `feat(backend): Workload analytics dashboard endpoint`
**Files touched:** `backend/app/routes/task_routes.py` (or new `analytics_routes.py`), `backend/app/main.py`, `backend/tests/test_tasks.py`

**Given starter code** — create `backend/app/routes/analytics_routes.py`:

```python
"""
Analytics routes — Manager-only endpoints for workload insights.
"""

from fastapi import APIRouter, Depends
from app.middleware.role_guard import require_role
from app.main import get_database

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/workload")
async def get_workload_dashboard(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Returns workload data for each employee:
    {
      "employees": [
        {
          "firebase_uid": "...",
          "name": "Ibrahim Raza",
          "total_tasks": 5,
          "weighted_load": 11,  // sum of complexity values
          "by_stage": {
            "todo": {"count": 1, "weight": 2},
            "in_progress": {"count": 2, "weight": 5},
            "submitted_for_review": {"count": 1, "weight": 3},
            "done": {"count": 1, "weight": 1}
          }
        }
      ]
    }
    """
    # IBRAHIM'S TASK: Implement this using MongoDB aggregation pipeline
    # Hint: Use $group with $sum and $cond, or iterate in Python
    pass
```

**Ibrahim's task:**
1. Implement the `get_workload_dashboard` endpoint using MongoDB aggregation
2. Register the router in `main.py`
3. Write tests verifying correct weight calculation
4. Handle edge case: employee with zero tasks should still appear with all zeros

**Expected response shape:**
```json
{
  "employees": [
    {
      "firebase_uid": "abc123",
      "name": "Ibrahim Raza",
      "total_tasks": 5,
      "weighted_load": 11,
      "by_stage": {
        "todo": {"count": 1, "weight": 2},
        "in_progress": {"count": 2, "weight": 5},
        "submitted_for_review": {"count": 1, "weight": 3},
        "done": {"count": 1, "weight": 1}
      }
    }
  ]
}
```

---

### Feature B3: Deadline & Overdue Escalation System

**Why it's substantial:** Tasks can now have optional deadlines. An endpoint flags overdue tasks. A background check (or on-demand endpoint) marks overdue tasks and notifies the manager.

**Branch:** `feature/backend/deadlines`
**PR Title:** `feat(backend): Deadline tracking and overdue escalation`
**Files touched:** `backend/app/models/task.py`, `backend/app/routes/task_routes.py`, `backend/tests/test_tasks.py`

**Given starter code** — add to `TaskCreate`:

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    assigned_to: str = Field(...)
    complexity: ComplexityType = Field(default=2)
    deadline: Optional[datetime] = Field(None, description="Optional deadline — ISO 8601 format")
```

**Ibrahim's task:**
1. Update `TaskCreate`, `TaskUpdate`, `TaskResponse` models to include `deadline` and `is_overdue` fields
2. Add `GET /api/tasks/overdue` endpoint (Manager only) that returns all non-done tasks past their deadline
3. On each `GET /api/tasks` call, dynamically compute `is_overdue` by comparing `deadline < now` for non-done tasks
4. Write tests with time-mocking to verify overdue detection

---

### Feature B4: Full Audit Trail

**Why it's substantial:** Every status transition is logged to a separate `audit_logs` collection with actor, action, timestamp, and before/after state. Full accountability chain.

**Branch:** `feature/backend/audit-trail`
**PR Title:** `feat(backend): Complete audit trail for all task transitions`
**Files touched:** `backend/app/utils/status_machine.py`, `backend/app/routes/task_routes.py`, new `backend/app/routes/audit_routes.py`, `backend/tests/test_tasks.py`

**Given starter code** — create `backend/app/models/audit.py`:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogEntry(BaseModel):
    task_id: str
    action: str  # "created", "started", "submitted", "confirmed", "rejected", "updated", "deleted"
    performed_by: str  # Firebase UID
    performed_by_name: str
    performed_by_role: str
    previous_stage: Optional[str] = None
    new_stage: Optional[str] = None
    details: Optional[str] = None  # e.g., rejection feedback
    timestamp: datetime
```

**Ibrahim's task:**
1. Create an `audit_log` helper function that inserts an `AuditLogEntry` into the `audit_logs` collection
2. Call this helper in every task route that changes state (create, start, submit, confirm, reject, update, delete)
3. Create `GET /api/tasks/{task_id}/audit` (Manager only) that returns the full audit trail for a task
4. Create `GET /api/audit/recent` (Manager only) that returns the last 50 audit entries across all tasks
5. Write tests verifying audit entries are created for each action

---

### Feature B5: Manager Analytics — Completion Metrics

**Why it's substantial:** A comprehensive analytics endpoint showing: completion rate per employee, average time from creation to done, rejection rate, and complexity distribution.

**Branch:** `feature/backend/manager-analytics`
**PR Title:** `feat(backend): Manager analytics — completion rates and performance metrics`
**Files touched:** `backend/app/routes/analytics_routes.py`, `backend/tests/test_tasks.py`

**Given starter code:**

```python
@router.get("/analytics/metrics")
async def get_completion_metrics(
    current_user: dict = Depends(require_role("manager")),
):
    """
    Returns:
    {
      "overall": {
        "total_tasks": 20,
        "completed": 12,
        "completion_rate": 0.6,
        "avg_completion_time_hours": 48.5,
        "rejection_rate": 0.25
      },
      "per_employee": [
        {
          "name": "Ibrahim Raza",
          "total": 10,
          "completed": 7,
          "completion_rate": 0.7,
          "avg_completion_time_hours": 36.2,
          "rejection_rate": 0.3,
          "complexity_distribution": {"1": 3, "2": 4, "3": 3}
        }
      ]
    }
    """
    # IBRAHIM'S TASK: Implement using MongoDB aggregation
    pass
```

**Ibrahim's task:** Full implementation of the aggregation pipeline, including handling division-by-zero edge cases, and calculating time deltas from `created_at` to the timestamp when stage became `done`.

---

## 6.2 — Saad (Frontend) — 5 Features

### Feature F1: Manager "Review Queue" Board (PR Inbox Style)

**Why it's substantial:** An enhanced inspection queue with: expanded task details on click, inline diff-like view of the submission, filtering by employee/complexity, and batch actions.

**Branch:** `feature/frontend/review-queue`
**PR Title:** `feat(frontend): Enhanced manager review queue with filtering and expanded details`
**Files touched:** `frontend/src/components/InspectionQueue.jsx`, `frontend/src/pages/ManagerDashboard.jsx`, `frontend/src/index.css`

**Given starter code** — add to `InspectionQueue.jsx`:

```jsx
// Filter state
const [filterEmployee, setFilterEmployee] = useState('all');
const [filterComplexity, setFilterComplexity] = useState('all');

// Filter bar JSX (add above the queue-list)
<div className="queue-filters" style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
  <div className="field" style={{ marginBottom: 0, flex: 1 }}>
    <label>Filter by Employee</label>
    <select value={filterEmployee} onChange={(e) => setFilterEmployee(e.target.value)}>
      <option value="all">All Employees</option>
      {/* SAAD'S TASK: Populate from unique assignees in tasks */}
    </select>
  </div>
  <div className="field" style={{ marginBottom: 0, flex: 1 }}>
    <label>Filter by Complexity</label>
    <select value={filterComplexity} onChange={(e) => setFilterComplexity(e.target.value)}>
      <option value="all">All</option>
      <option value="1">Low</option>
      <option value="2">Medium</option>
      <option value="3">High</option>
    </select>
  </div>
</div>
```

**Saad's task:**
1. Implement filtering logic — filter the `tasks` array before rendering
2. Add an expandable detail section when clicking a queue item (shows full description, assignee info, revision history if available)
3. Add a "Confirm All" batch action button that confirms all visible pending tasks
4. Style the filters and expanded view to match the Foreman design system (panel-raised backgrounds, hairline borders, mono fonts for metadata)
5. Add a loading state with the spinner while waiting for API responses

---

### Feature F2: Employee Workload View Grouped by Complexity

**Why it's substantial:** A new view for employees that groups their tasks by complexity instead of by stage, showing weighted progress bars and task counts.

**Branch:** `feature/frontend/workload-view`
**PR Title:** `feat(frontend): Employee workload view with complexity grouping`
**Files touched:** `frontend/src/pages/EmployeeDashboard.jsx`, new `frontend/src/components/WorkloadView.jsx`, `frontend/src/index.css`

**Given starter code** — create `frontend/src/components/WorkloadView.jsx`:

```jsx
import React from 'react';

export default function WorkloadView({ tasks }) {
  const byComplexity = {
    1: tasks.filter((t) => t.complexity === 1),
    2: tasks.filter((t) => t.complexity === 2),
    3: tasks.filter((t) => t.complexity === 3),
  };

  const labels = { 1: 'Low', 2: 'Medium', 3: 'High' };

  return (
    <div className="workload-view">
      {/* SAAD'S TASK:
        For each complexity level, render:
        1. A header showing "Low / Medium / High" with task count
        2. A progress bar showing % of tasks in "done" stage
        3. The ticket cards for that complexity level
        4. Add CSS for .workload-view, .workload-group, .progress-bar to index.css
        5. Add a toggle button in EmployeeDashboard to switch between
           "Board View" (existing) and "Workload View" (this component)
      */}
    </div>
  );
}
```

---

### Feature F3: Drag-and-Drop Stage Board (Respecting Role Permissions)

**Why it's substantial:** Tasks can be dragged between Kanban columns, but only if the transition is legal according to the status machine. Employees can only drag their own tasks through allowed transitions. Managers see all tasks but can only drag for manager-allowed transitions.

**Branch:** `feature/frontend/drag-drop`
**PR Title:** `feat(frontend): Drag-and-drop board with role-aware transition validation`
**Files touched:** `frontend/src/components/BoardColumn.jsx`, `frontend/src/components/TicketCard.jsx`, `frontend/src/pages/ManagerDashboard.jsx`, `frontend/src/pages/EmployeeDashboard.jsx`, `frontend/src/index.css`

**Given starter code:**

```jsx
// In TicketCard.jsx — add draggable attribute
<div
  className={`ticket ${isRework ? 'is-rework' : ''}`}
  draggable={isDraggable}
  onDragStart={(e) => {
    e.dataTransfer.setData('taskId', task.id);
    e.dataTransfer.setData('fromStage', task.stage);
    e.currentTarget.style.opacity = '0.5';
  }}
  onDragEnd={(e) => {
    e.currentTarget.style.opacity = '1';
  }}
>
```

```jsx
// In BoardColumn.jsx — add drop zone handlers
<div
  className={`column-body ${isOver ? 'drag-over' : ''}`}
  onDragOver={(e) => { e.preventDefault(); setIsOver(true); }}
  onDragLeave={() => setIsOver(false)}
  onDrop={(e) => {
    e.preventDefault();
    setIsOver(false);
    const taskId = e.dataTransfer.getData('taskId');
    const fromStage = e.dataTransfer.getData('fromStage');
    // SAAD'S TASK: Call onDrop(taskId, fromStage, stage) prop
    // The parent page handles the API call and validates the transition
  }}
>
```

**Saad's task:**
1. Implement the `isDraggable` logic — only draggable for legal transitions based on role
2. Add visual feedback: highlight valid drop targets when dragging, show red outline for invalid
3. Handle the drop event — call the appropriate API endpoint (`/start`, `/submit`, `/review`)
4. Add error handling for rejected transitions (show toast with error message)
5. Add CSS for `.drag-over` (amber border glow) and `.drag-invalid` (red border) states

---

### Feature F4: Dark Mode / Light Mode Toggle with Full Theming

**Why it's substantial:** A complete theming system with smooth transitions. The existing Foreman aesthetic (dark) becomes the default dark theme, and a new light theme is designed to complement it. Theme preference persists in localStorage.

**Branch:** `feature/frontend/dark-mode`
**PR Title:** `feat(frontend): Dark/light mode toggle with full theming system`
**Files touched:** `frontend/src/index.css`, `frontend/src/components/Topbar.jsx`, new `frontend/src/utils/theme.js`

**Given starter code** — create `frontend/src/utils/theme.js`:

```javascript
const STORAGE_KEY = 'foreman-theme';

export function getStoredTheme() {
  return localStorage.getItem(STORAGE_KEY) || 'dark';
}

export function setStoredTheme(theme) {
  localStorage.setItem(STORAGE_KEY, theme);
  document.documentElement.setAttribute('data-theme', theme);
}

export function initTheme() {
  const theme = getStoredTheme();
  document.documentElement.setAttribute('data-theme', theme);
}
```

**Saad's task:**
1. Define `[data-theme="light"]` CSS custom properties in `index.css` — redesign ALL color tokens for a light industrial aesthetic (think: light workshop, white paper tickets with darker shadows, etc.)
2. Add a theme toggle button in the Topbar (sun/moon icon)
3. Call `initTheme()` on app load in `App.jsx`
4. Ensure ALL components look correct in both themes — ticket cards, auth screen, modals, toasts, queue items
5. Add smooth CSS transitions for theme changes (`transition: background-color 0.3s, color 0.3s, border-color 0.3s`)

---

### Feature F5: Real-Time Notification System

**Why it's substantial:** A notification bell in the Topbar that shows unread notifications for: new task assignments (employee), task submissions awaiting review (manager), and confirm/reject results (employee). Uses polling (every 10 seconds) to simulate real-time.

**Branch:** `feature/frontend/notifications`
**PR Title:** `feat(frontend): Notification system for assignments, submissions, and reviews`
**Files touched:** new `frontend/src/components/NotificationBell.jsx`, `frontend/src/components/Topbar.jsx`, `frontend/src/index.css`

**Given starter code** — create `frontend/src/components/NotificationBell.jsx`:

```jsx
import React, { useState, useEffect, useRef } from 'react';
import api from '../utils/api';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const prevTasksRef = useRef([]);

  // SAAD'S TASK:
  // 1. Poll GET /api/tasks every 10 seconds
  // 2. Compare with previous state (prevTasksRef) to detect changes:
  //    - New task appeared (assigned to me) → "You were assigned: <title>"
  //    - Task stage changed to 'done' (was submitted_for_review) → "Approved: <title>"
  //    - Task stage changed to 'in_progress' with is_rejected=true → "Sent back: <title>"
  //    - Task stage changed to 'submitted_for_review' (for managers) → "Review requested: <title>"
  // 3. Store notifications in state with { id, message, time, read } shape
  // 4. Render a bell icon in Topbar with unread count badge
  // 5. Clicking bell opens a dropdown panel showing notification list
  // 6. Clicking a notification marks it as read
  // 7. "Mark all as read" button
  // 8. Style the dropdown, badge, and notification items matching Foreman design

  return (
    <div className="notification-bell" style={{ position: 'relative' }}>
      <button className="icon-btn" onClick={() => setDropdownOpen(!dropdownOpen)}>
        🔔
        {notifications.filter((n) => !n.read).length > 0 && (
          <span className="notif-badge">
            {notifications.filter((n) => !n.read).length}
          </span>
        )}
      </button>
      {/* SAAD'S TASK: Render dropdown panel here */}
    </div>
  );
}
```

---

## 6.3 — Ismail (DevOps) — 5 Features

### Feature D1: CI/CD Pipeline with Test Gating and Build Caching

**Why it's substantial:** A complete GitHub Actions CI pipeline that: installs deps, lints, runs tests, builds Docker images, and uses layer caching to speed up builds. The pipeline must gate PRs — all checks must pass before merge is possible.

**Branch:** `feature/devops/ci-pipeline`
**PR Title:** `feat(devops): CI pipeline with lint, test, build, and caching`
**Files touched:** `.github/workflows/ci.yml`, `.github/workflows/cd.yml`

**Given starter code** — `.github/workflows/ci.yml`:

```yaml
name: CI — Lint, Test, Build

on:
  pull_request:
    branches: [develop, main]

jobs:
  backend-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: 'backend/requirements.txt'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install ruff

      - name: Lint with Ruff
        run: |
          cd backend
          ruff check app/

      # ISMAIL'S TASK:
      # - Add a step to run pytest with proper configuration
      #   (need to handle the Firebase/MongoDB mocking for CI)
      # - Add a step to build the backend Docker image (no push)
      # - Add Docker layer caching using actions/cache

  frontend-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      # ISMAIL'S TASK:
      # - Add ESLint step
      # - Add build step (npm run build)
      # - Add Docker image build step
      # - Configure proper environment variables for the build
```

**Ismail's task:**
1. Complete both job definitions with all steps
2. Add Docker layer caching using `docker/build-push-action` with `cache-from/cache-to`
3. Create mock/stub Firebase and MongoDB configurations for CI test environment
4. Set up the CD pipeline (`cd.yml`) triggered on merge to `main`
5. Ensure branch protection rules reference these workflow checks

---

### Feature D2: Kubernetes Horizontal Pod Autoscaling

**Why it's substantial:** Configure HPA for both frontend and backend deployments based on CPU utilization. Includes metrics server setup, load testing to trigger scaling, and monitoring commands.

**Branch:** `feature/devops/hpa`
**PR Title:** `feat(devops): Horizontal Pod Autoscaler for backend and frontend`
**Files touched:** `k8s/hpa.yml`, `k8s/backend-deployment.yml`, `k8s/frontend-deployment.yml`

**Given starter code** — `k8s/hpa.yml`:

```yaml
# ISMAIL'S TASK: Create HPA resources for backend and frontend
# Requirements:
# 1. Backend HPA:
#    - Min replicas: 1
#    - Max replicas: 5
#    - Target CPU utilization: 70%
#    - Scale-down stabilization: 60 seconds
#
# 2. Frontend HPA:
#    - Min replicas: 1
#    - Max replicas: 3
#    - Target CPU utilization: 80%
#
# 3. Add resource requests/limits to both deployments:
#    - Backend: requests 100m CPU, 128Mi RAM; limits 500m CPU, 512Mi RAM
#    - Frontend: requests 50m CPU, 64Mi RAM; limits 200m CPU, 256Mi RAM
#
# 4. Document the commands to:
#    - Enable metrics-server in minikube
#    - Verify HPA status
#    - Generate load to trigger scaling
#    - Watch pods scale up and down
```

---

### Feature D3: Centralized Logging with EFK Stack (Simplified)

**Why it's substantial:** Set up a logging pipeline using a simplified Fluentd → ElasticSearch → Kibana stack (or a simpler Loki + Grafana alternative) for the local K8s cluster. All pod logs are collected, tagged by service, and viewable in a dashboard.

**Branch:** `feature/devops/centralized-logging`
**PR Title:** `feat(devops): Centralized logging with log aggregation`
**Files touched:** new `k8s/logging/` directory with multiple manifests

**Ismail's task:**
1. Choose and implement a logging stack (recommended: Loki + Grafana for simplicity on free tiers)
2. Create K8s manifests for the logging infrastructure
3. Configure log collection from backend and frontend pods
4. Set up a basic Grafana dashboard showing: logs by service, error rate, log volume over time
5. Document how each team member can query logs for their own service
6. Write a troubleshooting guide: "How to find why your pod crashed using the logging dashboard"

---

### Feature D4: Automated Cloud Deployment Pipeline with Rollback

**Why it's substantial:** A GitHub Actions CD pipeline that: builds images, pushes to DockerHub, deploys frontend to Vercel, deploys backend to Render, runs a smoke test against the deployed services, and automatically rolls back if the smoke test fails.

**Branch:** `feature/devops/cloud-cd`
**PR Title:** `feat(devops): Automated cloud deployment with smoke tests and rollback`
**Files touched:** `.github/workflows/cd.yml`, new `.github/workflows/rollback.yml`

**Given starter code** — `.github/workflows/cd.yml`:

```yaml
name: CD — Build, Push, Deploy to Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # ISMAIL'S TASK:
      # 1. Build and push backend image to DockerHub
      # 2. Build and push frontend image to DockerHub
      # 3. Deploy frontend to Vercel (via Vercel CLI or deploy hook)
      # 4. Deploy backend to Render (via deploy hook)
      # 5. Wait for deployments to be live (add a sleep + health check loop)
      # 6. Run smoke test:
      #    - curl the deployed backend /api/health
      #    - curl the deployed frontend URL
      # 7. If smoke test fails → trigger rollback workflow
      # 8. Post deployment status to a Slack webhook or GitHub comment
```

---

### Feature D5: Automated Image Vulnerability Scanning

**Why it's substantial:** Integrate Docker image vulnerability scanning into the CI pipeline using Trivy. Block PRs if critical/high vulnerabilities are found. Generate a security report as a PR comment.

**Branch:** `feature/devops/vulnerability-scanning`
**PR Title:** `feat(devops): Docker image vulnerability scanning with Trivy`
**Files touched:** `.github/workflows/ci.yml`, new `.github/workflows/security-scan.yml`

**Given starter code:**

```yaml
# Add to ci.yml or create security-scan.yml

# ISMAIL'S TASK:
# 1. Use aquasecurity/trivy-action to scan both Docker images
# 2. Configure severity threshold: CRITICAL, HIGH
# 3. If vulnerabilities found:
#    - Generate a summary table
#    - Post as a PR comment using github-script action
#    - Fail the job (block merge)
# 4. If clean: post a "✅ No vulnerabilities found" comment
# 5. Generate SBOM (Software Bill of Materials) as a CI artifact
```

---

# PHASE 7 — Docker (All Members, Same Toolset)

## 7.1 — Backend Dockerfile (Multi-Stage)

### `backend/Dockerfile`

```dockerfile
# ─── Stage 1: Builder ───
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies in a virtual environment for clean copy
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Production ───
FROM python:3.12-slim AS production

# Security: run as non-root user
RUN groupadd -r foreman && useradd -r -g foreman foreman

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/

# The serviceAccountKey.json is mounted at runtime, not baked into the image
# This is a security best practice

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Switch to non-root user
USER foreman

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `backend/.dockerignore`

```
__pycache__/
*.py[cod]
venv/
.venv/
.env
.env.*
serviceAccountKey.json
tests/
.git/
.github/
*.md
```

## 7.2 — Frontend Dockerfile (Multi-Stage)

### `frontend/Dockerfile`

```dockerfile
# ─── Stage 1: Build ───
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first (leverage Docker layer caching)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .

# Build-time environment variables (baked into the static bundle)
ARG VITE_API_URL
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID

RUN npm run build

# ─── Stage 2: Nginx ───
FROM nginx:1.25-alpine AS production

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### `frontend/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — fallback to index.html for client-side routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### `frontend/.dockerignore`

```
node_modules/
dist/
.env
.env.*
.git/
.github/
*.md
```

## 7.3 — Docker Compose (Full Stack)

### `docker-compose.yml`

```yaml
version: '3.9'

services:
  # ─── MongoDB ───
  mongo:
    image: mongo:7
    container_name: foreman-mongo
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    networks:
      - foreman-net
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.runCommand({ping:1})"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ─── Backend (FastAPI) ───
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: foreman-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/foreman_db
      - FIREBASE_SERVICE_ACCOUNT_PATH=/app/serviceAccountKey.json
      - FRONTEND_URL=http://localhost
    volumes:
      - ./backend/serviceAccountKey.json:/app/serviceAccountKey.json:ro
    depends_on:
      mongo:
        condition: service_healthy
    networks:
      - foreman-net
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ─── Frontend (React + Nginx) ───
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: http://localhost:8000
        VITE_FIREBASE_API_KEY: ${VITE_FIREBASE_API_KEY}
        VITE_FIREBASE_AUTH_DOMAIN: ${VITE_FIREBASE_AUTH_DOMAIN}
        VITE_FIREBASE_PROJECT_ID: ${VITE_FIREBASE_PROJECT_ID}
        VITE_FIREBASE_STORAGE_BUCKET: ${VITE_FIREBASE_STORAGE_BUCKET}
        VITE_FIREBASE_MESSAGING_SENDER_ID: ${VITE_FIREBASE_MESSAGING_SENDER_ID}
        VITE_FIREBASE_APP_ID: ${VITE_FIREBASE_APP_ID}
    container_name: foreman-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - foreman-net
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80/"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  mongo-data:
    name: foreman-mongo-data

networks:
  foreman-net:
    name: foreman-network
    driver: bridge
```

## 7.4 — Docker Commands Reference (All Members Use These)

```bash
# ─── Build ───
docker compose build                    # Build all services
docker compose build backend            # Build only backend
docker compose build frontend           # Build only frontend

# ─── Run ───
docker compose up -d                    # Start all in background
docker compose up                       # Start with logs in foreground
docker compose up backend mongo         # Start specific services

# ─── Verify ───
docker compose ps                       # Check status of all services
docker compose logs backend             # View backend logs
docker compose logs -f frontend         # Follow frontend logs in real time
docker compose exec backend sh          # Shell into backend container

# ─── Stop & Clean ───
docker compose down                     # Stop and remove containers
docker compose down -v                  # Also remove volumes (⚠️ deletes DB data)
docker compose down --rmi local         # Also remove built images

# ─── Standalone Container (Individual Testing) ───
docker build -t foreman-backend:dev ./backend
docker run -d --name test-backend -p 8000:8000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/foreman_db" \
  foreman-backend:dev

docker build -t foreman-frontend:dev ./frontend
docker run -d --name test-frontend -p 3000:80 foreman-frontend:dev
```

---

# PHASE 8 — Security, Auth & RBAC Deep Dive

## 8.1 — Security Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: FIREBASE AUTHENTICATION                               │
│  ├── Email/Password signup with email verification              │
│  ├── Firebase issues ID tokens (JWT, 1-hour expiry)             │
│  └── Client sends token in Authorization: Bearer <token>       │
│                                                                  │
│  Layer 2: BACKEND TOKEN VERIFICATION                            │
│  ├── firebase-admin SDK verifies token signature + expiry       │
│  ├── Extracts uid from token                                    │
│  └── 401 Unauthorized if invalid/expired/missing                │
│                                                                  │
│  Layer 3: ROLE LOOKUP (MongoDB)                                 │
│  ├── Looks up user document by firebase_uid                     │
│  ├── Retrieves role field (manager / employee)                  │
│  └── 404 if user not registered                                 │
│                                                                  │
│  Layer 4: ROLE ENFORCEMENT (require_role middleware)             │
│  ├── Compares user.role with required role                      │
│  ├── 403 Forbidden if role mismatch                             │
│  └── Returns user document to route handler if OK               │
│                                                                  │
│  Layer 5: DATA SCOPING (Route Logic)                            │
│  ├── Manager: sees ALL tasks                                    │
│  ├── Employee: sees only assigned_to == their uid               │
│  └── Status machine: only assigned employee can submit          │
│                                                                  │
│  Layer 6: STATUS MACHINE (Server-Side Enforcement)              │
│  ├── validate_transition() checks legal stage changes           │
│  ├── TRANSITION_ROLES dict enforces WHO can trigger each        │
│  └── Prevents: employee self-approve, skip stages, etc.         │
│                                                                  │
│  Layer 7: SECRET MANAGEMENT                                     │
│  ├── .gitignore: .env, serviceAccountKey.json                   │
│  ├── Docker: mounted as volume (not baked into image)           │
│  ├── K8s: Secrets (base64-encoded, mounted as env/volume)       │
│  ├── GitHub Actions: Repository Secrets                          │
│  └── Cloud: Platform env vars (Render dashboard, Vercel dashboard)│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 8.2 — Secret Handling Matrix

| Secret | `.gitignore`? | Docker | K8s | GitHub Actions | Cloud Platform |
|--------|:---:|:---:|:---:|:---:|:---:|
| `serviceAccountKey.json` | ✅ | Volume mount (`-v`) | K8s Secret (base64) | `FIREBASE_SA_JSON` secret | Render env var (as JSON string) |
| `MONGO_URI` | ✅ (in `.env`) | `environment:` in compose | K8s Secret (base64) | `MONGO_URI` secret | Render env var |
| Firebase web config | ✅ (in `.env`) | Build args | ConfigMap | Build-time secrets | Vercel env vars |
| DockerHub credentials | N/A | N/A | N/A | `DOCKERHUB_USERNAME/TOKEN` | N/A |

## 8.3 — Status Machine — Server-Side Enforcement (Complete)

The status machine in `backend/app/utils/status_machine.py` (shown in Phase 1) is the **core security feature**. Here's why each rule matters:

| Transition | Who | Why |
|-----------|-----|-----|
| `todo → in_progress` | Employee only | Employee acknowledges and starts work |
| `in_progress → submitted_for_review` | Employee only | Employee declares work is done (like opening a PR) |
| `submitted_for_review → done` | **Manager only** | Manager confirms/approves (like merging a PR) |
| `submitted_for_review → in_progress` | **Manager only** | Manager rejects with feedback (like requesting changes) |
| `done → anything` | **Nobody** | Terminal state — once signed off, it's done |
| `todo → done` | **Nobody** | Can't skip steps — must go through the workflow |

**Server-side enforcement means:**
- Even if someone modifies the frontend JavaScript to send a "confirm" request, the backend will reject it with 403 if they're not a Manager
- Even if an Employee crafts a direct HTTP request to skip from `todo` to `done`, the status machine will reject it with 400
- The UI simply reflects what the backend allows — it's **defense in depth**

---

# PHASE 9 — CI/CD Pipeline (GitHub Actions)

## 9.1 — CI Pipeline (On Pull Request)

### `.github/workflows/ci.yml`

```yaml
name: CI — Lint, Test, Build

on:
  pull_request:
    branches: [develop, main]

env:
  PYTHON_VERSION: '3.12'
  NODE_VERSION: '20'

jobs:
  # ─── Backend Checks ───
  backend:
    name: Backend — Lint, Test, Build
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: 'backend/requirements.txt'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install ruff

      - name: Lint with Ruff
        run: ruff check app/ --output-format=github

      - name: Run tests
        run: |
          python -m pytest tests/ -v --tb=short
        env:
          MONGO_URI: mongodb://localhost:27017/foreman_test_db
          FIREBASE_SERVICE_ACCOUNT_PATH: ./tests/mock_sa.json

      - name: Build Docker image
        run: docker build -t foreman-backend:ci-${{ github.sha }} .

  # ─── Frontend Checks ───
  frontend:
    name: Frontend — Lint, Build
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          VITE_API_URL: https://placeholder.onrender.com
          VITE_FIREBASE_API_KEY: ci-placeholder
          VITE_FIREBASE_AUTH_DOMAIN: ci.firebaseapp.com
          VITE_FIREBASE_PROJECT_ID: ci-project
          VITE_FIREBASE_STORAGE_BUCKET: ci.appspot.com
          VITE_FIREBASE_MESSAGING_SENDER_ID: '000000'
          VITE_FIREBASE_APP_ID: 'ci-app-id'

      - name: Build Docker image
        run: |
          docker build -t foreman-frontend:ci-${{ github.sha }} \
            --build-arg VITE_API_URL=https://placeholder.onrender.com \
            --build-arg VITE_FIREBASE_API_KEY=ci-placeholder \
            --build-arg VITE_FIREBASE_AUTH_DOMAIN=ci.firebaseapp.com \
            --build-arg VITE_FIREBASE_PROJECT_ID=ci-project \
            --build-arg VITE_FIREBASE_STORAGE_BUCKET=ci.appspot.com \
            --build-arg VITE_FIREBASE_MESSAGING_SENDER_ID=000000 \
            --build-arg VITE_FIREBASE_APP_ID=ci-app-id \
            .
```

## 9.2 — CD Pipeline (On Merge to Main)

### `.github/workflows/cd.yml`

```yaml
name: CD — Build, Push, Deploy

on:
  push:
    branches: [main]

env:
  DOCKERHUB_REPO_BACKEND: ${{ secrets.DOCKERHUB_USERNAME }}/foreman-backend
  DOCKERHUB_REPO_FRONTEND: ${{ secrets.DOCKERHUB_USERNAME }}/foreman-frontend

jobs:
  deploy:
    name: Build, Push, Deploy to Cloud
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.DOCKERHUB_REPO_BACKEND }}:latest
            ${{ env.DOCKERHUB_REPO_BACKEND }}:${{ github.sha }}

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ env.DOCKERHUB_REPO_FRONTEND }}:latest
            ${{ env.DOCKERHUB_REPO_FRONTEND }}:${{ github.sha }}
          build-args: |
            VITE_API_URL=${{ secrets.PRODUCTION_API_URL }}
            VITE_FIREBASE_API_KEY=${{ secrets.FIREBASE_API_KEY }}
            VITE_FIREBASE_AUTH_DOMAIN=${{ secrets.FIREBASE_AUTH_DOMAIN }}
            VITE_FIREBASE_PROJECT_ID=${{ secrets.FIREBASE_PROJECT_ID }}
            VITE_FIREBASE_STORAGE_BUCKET=${{ secrets.FIREBASE_STORAGE_BUCKET }}
            VITE_FIREBASE_MESSAGING_SENDER_ID=${{ secrets.FIREBASE_MESSAGING_SENDER_ID }}
            VITE_FIREBASE_APP_ID=${{ secrets.FIREBASE_APP_ID }}

      - name: Deploy backend to Render
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
          echo "Backend deploy triggered — Render will pull latest from DockerHub"

      - name: Deploy frontend to Vercel
        run: |
          npm i -g vercel
          cd frontend
          vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }} --yes

      - name: Smoke test — Backend health check
        run: |
          echo "Waiting 60s for deployments to propagate..."
          sleep 60
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.PRODUCTION_API_URL }}/api/health)
          if [ "$STATUS" != "200" ]; then
            echo "❌ Backend health check failed with status $STATUS"
            exit 1
          fi
          echo "✅ Backend is healthy"

      - name: Smoke test — Frontend availability
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.PRODUCTION_FRONTEND_URL }})
          if [ "$STATUS" != "200" ]; then
            echo "❌ Frontend not reachable, status $STATUS"
            exit 1
          fi
          echo "✅ Frontend is live"
```

## 9.3 — Required GitHub Secrets

Go to GitHub → Repository → Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|------------|-------|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token (not password) |
| `RENDER_DEPLOY_HOOK_URL` | From Render dashboard → Deploy Hook URL |
| `VERCEL_TOKEN` | From Vercel → Settings → Tokens |
| `PRODUCTION_API_URL` | e.g., `https://foreman-api.onrender.com` |
| `PRODUCTION_FRONTEND_URL` | e.g., `https://foreman-kanban.vercel.app` |
| `FIREBASE_API_KEY` | From Firebase console |
| `FIREBASE_AUTH_DOMAIN` | From Firebase console |
| `FIREBASE_PROJECT_ID` | From Firebase console |
| `FIREBASE_STORAGE_BUCKET` | From Firebase console |
| `FIREBASE_MESSAGING_SENDER_ID` | From Firebase console |
| `FIREBASE_APP_ID` | From Firebase console |

## 9.4 — Every Member Triggers CI At Least Once

Each team member must:

1. Create a feature branch
2. Make a change (even a small one to start — like adding a comment)
3. Push the branch
4. Open a PR
5. Watch the CI pipeline run in the Actions tab
6. If it fails → read the error log → fix it → push again
7. See it pass → Ismail merges

This ensures every team member has personally experienced the CI feedback loop.

---

# PHASE 10 — Kubernetes (Local Learning Cluster)

## 10.1 — Minikube Setup

```bash
# Start minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify
minikube status
# Expected:
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

## 10.2 — Namespace

### `k8s/namespace.yml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: foreman
  labels:
    app: foreman
    environment: development
```

```bash
kubectl apply -f k8s/namespace.yml
# Expected: namespace/foreman created

kubectl get namespaces
# Expected: foreman   Active   Xs
```

## 10.3 — ConfigMap

### `k8s/configmap.yml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: foreman-config
  namespace: foreman
data:
  FRONTEND_URL: "http://foreman.local"
  API_URL: "http://backend-svc:8000"
```

## 10.4 — Secrets

### `k8s/secrets.yml`

```yaml
# TEMPLATE — replace base64 values with your actual encoded secrets
# To encode: echo -n "your-value" | base64
# NEVER commit this file with real values

apiVersion: v1
kind: Secret
metadata:
  name: foreman-secrets
  namespace: foreman
type: Opaque
data:
  MONGO_URI: bW9uZ29kYitzcnY6Ly9mb3JlbWFuLWFkbWluOnBhc3N3b3JkQGZvcmVtYW4tY2x1c3Rlci54eHh4eC5tb25nb2RiLm5ldC9mb3JlbWFuX2RiP3JldHJ5V3JpdGVzPXRydWUmdz1tYWpvcml0eQ==
  # The above is a placeholder — replace with: echo -n "your-real-mongo-uri" | base64

---

apiVersion: v1
kind: Secret
metadata:
  name: firebase-sa-secret
  namespace: foreman
type: Opaque
data:
  serviceAccountKey.json: |
    # Base64-encode your entire serviceAccountKey.json:
    # cat serviceAccountKey.json | base64 -w 0
    # Paste the output here
    <BASE64_ENCODED_SERVICE_ACCOUNT_JSON>
```

## 10.5 — MongoDB (Local K8s with PersistentVolume)

### `k8s/mongo-pv.yml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongo-pv
  namespace: foreman
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/mongo
    type: DirectoryOrCreate

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-pvc
  namespace: foreman
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

### `k8s/mongo-deployment.yml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongo
  namespace: foreman
  labels:
    app: mongo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
        - name: mongo
          image: mongo:7
          ports:
            - containerPort: 27017
          volumeMounts:
            - name: mongo-storage
              mountPath: /data/db
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: mongo-storage
          persistentVolumeClaim:
            claimName: mongo-pvc

---

apiVersion: v1
kind: Service
metadata:
  name: mongo-svc
  namespace: foreman
spec:
  selector:
    app: mongo
  ports:
    - port: 27017
      targetPort: 27017
  type: ClusterIP
```

## 10.6 — Backend Deployment

### `k8s/backend-deployment.yml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: foreman
  labels:
    app: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: foreman-backend:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: MONGO_URI
              valueFrom:
                secretKeyRef:
                  name: foreman-secrets
                  key: MONGO_URI
            - name: FIREBASE_SERVICE_ACCOUNT_PATH
              value: "/secrets/serviceAccountKey.json"
            - name: FRONTEND_URL
              valueFrom:
                configMapKeyRef:
                  name: foreman-config
                  key: FRONTEND_URL
          volumeMounts:
            - name: firebase-sa
              mountPath: /secrets
              readOnly: true
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: firebase-sa
          secret:
            secretName: firebase-sa-secret

---

apiVersion: v1
kind: Service
metadata:
  name: backend-svc
  namespace: foreman
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

## 10.7 — Frontend Deployment

### `k8s/frontend-deployment.yml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: foreman
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: foreman-frontend:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 30
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "256Mi"
              cpu: "200m"

---

apiVersion: v1
kind: Service
metadata:
  name: frontend-svc
  namespace: foreman
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

## 10.8 — Ingress

### `k8s/ingress.yml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: foreman-ingress
  namespace: foreman
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: foreman.local
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend-svc
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
```

## 10.9 — Deploy Everything

```bash
# Build images for minikube's Docker daemon
eval $(minikube docker-env)
docker build -t foreman-backend:latest ./backend
docker build -t foreman-frontend:latest ./frontend \
  --build-arg VITE_API_URL=http://foreman.local \
  --build-arg VITE_FIREBASE_API_KEY=your-key \
  --build-arg VITE_FIREBASE_AUTH_DOMAIN=your-domain \
  --build-arg VITE_FIREBASE_PROJECT_ID=your-project \
  --build-arg VITE_FIREBASE_STORAGE_BUCKET=your-bucket \
  --build-arg VITE_FIREBASE_MESSAGING_SENDER_ID=your-id \
  --build-arg VITE_FIREBASE_APP_ID=your-app-id

# Apply all manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/mongo-pv.yml
kubectl apply -f k8s/mongo-deployment.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/ingress.yml

# Verify all pods are running
kubectl get all -n foreman
# Expected:
# pod/backend-xxxxx      1/1   Running   0          Xs
# pod/backend-yyyyy      1/1   Running   0          Xs
# pod/frontend-xxxxx     1/1   Running   0          Xs
# pod/frontend-yyyyy     1/1   Running   0          Xs
# pod/mongo-xxxxx        1/1   Running   0          Xs

# Add foreman.local to hosts file
# Windows (run as Administrator):
echo "$(minikube ip) foreman.local" >> C:\Windows\System32\drivers\etc\hosts

# Mac/Linux:
echo "$(minikube ip) foreman.local" | sudo tee -a /etc/hosts

# Open in browser:
# http://foreman.local
```

## 10.10 — Scaling & Troubleshooting (Each Member)

### Scale your service

```bash
# Ibrahim scales backend
kubectl scale deployment backend -n foreman --replicas=3
kubectl get pods -n foreman -l app=backend
# Expected: 3 backend pods

# Saad scales frontend
kubectl scale deployment frontend -n foreman --replicas=3
kubectl get pods -n foreman -l app=frontend
```

### Read logs

```bash
# Ibrahim checks backend logs
kubectl logs -n foreman -l app=backend --tail=50

# Saad checks frontend logs
kubectl logs -n foreman -l app=frontend --tail=50
```

### Deliberately break & fix

```bash
# Break: Set wrong image tag
kubectl set image deployment/backend backend=foreman-backend:BROKEN -n foreman

# Diagnose:
kubectl get pods -n foreman
# Expected: ImagePullBackOff or ErrImagePull

kubectl describe pod <pod-name> -n foreman
# Events section shows the error

# Fix:
kubectl set image deployment/backend backend=foreman-backend:latest -n foreman
kubectl rollout status deployment/backend -n foreman
# Expected: deployment "backend" successfully rolled out
```

---

# PHASE 11 — Free Cloud Deployment (Multi-User Public Access)

## 11.1 — Frontend → Vercel (Free Tier)

### Step 1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com) → **Sign Up** with GitHub
2. Authorize Vercel to access your GitHub account

### Step 2: Import Project

1. Click **"Add New..."** → **Project**
2. Import the `foreman-kanban` repository from GitHub
3. **Framework Preset:** Vite
4. **Root Directory:** `frontend` (click "Edit" and type `frontend`)
5. **Build Command:** `npm run build`
6. **Output Directory:** `dist`

### Step 3: Configure Environment Variables

In the Vercel project settings → **Environment Variables** → Add each:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://foreman-api.onrender.com` (you'll get this from Render in Step 11.2) |
| `VITE_FIREBASE_API_KEY` | Your Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | `foreman-kanban.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | `foreman-kanban` |
| `VITE_FIREBASE_STORAGE_BUCKET` | `foreman-kanban.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Your sender ID |
| `VITE_FIREBASE_APP_ID` | Your app ID |

### Step 4: Deploy

1. Click **Deploy**
2. Wait ~1-2 minutes for build
3. **Your frontend is live at:** `https://foreman-kanban.vercel.app` (or similar)
4. Every push to `main` will auto-deploy

### Step 5: Add `vercel.json` for SPA Routing

Create `frontend/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## 11.2 — Backend → Render (Free Tier)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com) → **Get Started for Free** → Sign up with GitHub

### Step 2: Create Web Service

1. Click **"New +"** → **Web Service**
2. Connect your `foreman-kanban` repository
3. Configuration:
   - **Name:** `foreman-api`
   - **Region:** Oregon (US West) or Frankfurt (EU)
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** **Free**

### Step 3: Configure Environment Variables

In the Render dashboard → your service → **Environment** → Add:

| Key | Value |
|-----|-------|
| `MONGO_URI` | Your MongoDB Atlas connection string (full URI) |
| `FRONTEND_URL` | `https://foreman-kanban.vercel.app` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Paste the entire contents of `serviceAccountKey.json` as a single line |
| `PYTHON_VERSION` | `3.12.0` |

> [!WARNING]
> **Render Free Tier Caveats:**
> - Service sleeps after **15 minutes** of inactivity
> - Cold start takes **30-60 seconds** on first request after sleep
> - 750 hours/month free (enough for one always-on service, but shared across all free services)
>
> Frame these as **learning points**: this mirrors real-world serverless cold-start behavior. In production, you'd use a paid tier or a keep-alive ping.

### Step 4: Handle Firebase SA as Environment Variable

Since you can't upload a file to Render, modify `backend/app/firebase_auth.py` to support loading from env var:

```python
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from app.config import FIREBASE_SERVICE_ACCOUNT_PATH

# Support both: file path (local/Docker) and JSON string (cloud env var)
sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
if sa_json:
    # Cloud deployment: SA JSON is an environment variable
    sa_dict = json.loads(sa_json)
    cred = credentials.Certificate(sa_dict)
else:
    # Local/Docker: SA JSON is a file
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)

firebase_admin.initialize_app(cred)
```

### Step 5: Get the Deploy Hook URL

1. In Render dashboard → your service → **Settings** → scroll to **Deploy Hook**
2. Copy the URL — this is `RENDER_DEPLOY_HOOK_URL` for GitHub Actions

### Step 6: Your Backend URL

After the first deploy completes:
- **Your backend is live at:** `https://foreman-api.onrender.com`
- Test: `curl https://foreman-api.onrender.com/api/health`
- Expected: `{"status":"healthy","service":"foreman-backend"}`

## 11.3 — Configure CORS Between Deployed Services

Update the Vercel environment variable:
- `VITE_API_URL` → `https://foreman-api.onrender.com`

Update the Render environment variable:
- `FRONTEND_URL` → `https://foreman-kanban.vercel.app`

The backend's CORS middleware (`main.py`) uses `FRONTEND_URL` to allow cross-origin requests. Both services need to know each other's URLs.

## 11.4 — Firebase Auth — Add Authorized Domains

1. Go to Firebase Console → Authentication → Settings
2. Under **Authorized domains**, add:
   - `foreman-kanban.vercel.app`
   - `foreman-api.onrender.com`
3. These are needed for Firebase Auth to work from the deployed frontend

## 11.5 — MongoDB Atlas — Already Configured

Since we set `0.0.0.0/0` in Network Access during Phase 1, both the Render backend and local development can connect. No changes needed.

## 11.6 — End-to-End Cloud Verification

1. Open `https://foreman-kanban.vercel.app` in your browser
2. Create a Manager account → verify the Foreman auth screen renders with the industrial aesthetic
3. In a different browser/incognito → create an Employee account
4. As Manager: create a task, assign to the employee
5. As Employee: start → submit for inspection
6. As Manager: confirm → verify stamp animation and "Signed Off ✓"
7. Share the URL with classmates → they can sign up and use it simultaneously

> [!TIP]
> **Free-tier limitations as learning points:**
> - **Render cold starts:** First request after 15 min takes 30-60 seconds. This mirrors serverless cold-start behavior (AWS Lambda, Google Cloud Run). In production, you'd use provisioned concurrency or a paid always-on tier.
> - **MongoDB Atlas M0:** 512 MB storage, shared resources. Fine for learning, but real apps need M2+ with dedicated resources.
> - **Vercel:** 100 GB bandwidth/month on free tier. More than enough for a class project.

---

# PHASE 12 — Submission & Evaluation

## 12.1 — Rubric

| Category | Weight | Criteria | Marks |
|----------|--------|----------|-------|
| **Git & Version Control** | 15% | Branch strategy followed, meaningful commits, PR template used, Ismail-only merges, branch protection configured | /15 |
| **Docker** | 15% | Multi-stage Dockerfiles, docker-compose with healthchecks/volumes/networks, each member builds & runs independently, deliberate break-fix documented | /15 |
| **CI/CD Pipeline** | 15% | GitHub Actions CI on PR (lint/test/build), CD on merge to main (push/deploy), each member triggers CI at least once, pipeline failure fixed | /15 |
| **Kubernetes** | 15% | Namespace, ConfigMap, Secrets, Deployments, Services, PV/PVC, Ingress, probes, each member deploys & scales locally, break-fix documented | /15 |
| **Security & RBAC** | 10% | Firebase Auth working, email verification, server-side token verification, role guard middleware with proper 401/403, status machine enforced server-side, secrets never committed | /10 |
| **Cloud Deployment** | 10% | Frontend on Vercel, backend on Render, MongoDB Atlas, CORS configured, public URL accessible, auto-deploy from main, free-tier caveats documented | /10 |
| **Feature Completeness** | 15% | 5 features per person implemented (15 total), each on its own branch with PR, code quality, tests where applicable | /15 |
| **Demo & Documentation** | 5% | Live demo showing both roles, README with setup instructions, architecture diagrams, individual DevOps log showing personal Docker/K8s work | /5 |
| **TOTAL** | **100%** | | **/100** |

## 12.2 — Submission Checklist

- [ ] **GitHub Repository** is public (or shared with instructor)
- [ ] **Branch protection** rules are configured on `main` and `develop`
- [ ] **All PRs** are visible in the repository's Pull Requests tab (15 feature PRs + initial setup)
- [ ] **CI pipeline** has at least one green run per team member
- [ ] **CD pipeline** has at least one successful deploy to cloud
- [ ] **Docker images** are on DockerHub (public or shared)
- [ ] **K8s manifests** are in the `k8s/` directory
- [ ] **Cloud deployment** is live and accessible:
  - Frontend URL: `https://foreman-kanban.vercel.app`
  - Backend URL: `https://foreman-api.onrender.com`
- [ ] **README.md** includes:
  - Project overview
  - Architecture diagram
  - Setup instructions (local + Docker + K8s)
  - Cloud URLs
  - Team member responsibilities
- [ ] **No secrets committed** — verify with: `git log --all -p | grep -i "serviceAccountKey\|mongodb+srv\|apiKey"` (should return nothing)
- [ ] **Individual DevOps logs** — each member submits a short document showing:
  - Their Docker build/run/debug commands and output
  - Their K8s deploy/scale/debug commands and output
  - A CI failure they encountered and how they fixed it
- [ ] **Live demo prepared** — 10-minute walkthrough showing:
  1. Manager creates account and assigns a task
  2. Employee receives task, starts it, submits for review
  3. Manager confirms (stamp animation visible)
  4. Manager rejects another task with feedback
  5. Employee sees rejection feedback, reworks, resubmits
  6. Show the Kubernetes dashboard with pods running
  7. Show the CI/CD pipeline in GitHub Actions
  8. Scale a deployment live during the demo

---

> **End of Walkthrough — Phase 0 through Phase 12 Complete**
>
> This document represents the entire journey from an empty Git repository to a fully running, role-based, Firebase-secured, three-tier, containerized, Kubernetes-deployed, CI/CD-automated, and publicly cloud-hosted application.
>
> Manager and Employee accounts can both sign up and use the system from anywhere in the world via the public Vercel + Render deployment.
>
> The Foreman industrial aesthetic — dark panels, amber accents, paper tickets with pins, and stamp animations — carries through every screen, making the system visually distinctive and true to its workshop metaphor.
