# Developer Guide & Codebase Architecture

> **Foreman Kanban** — Architecture patterns, code standards, state machine internals, and extension guides for developers.

---

## 1. Project Organization

Foreman Kanban is organized as a modern monorepo separating frontend presentation, backend REST API, container definitions, and Kubernetes orchestration:

```
foreman-kanban/
├── .github/workflows/          # CI/CD Workflows (ci.yml, cd.yml)
├── assets/                     # Visual diagrams, SVG UI mockups & media
├── docs/                       # Technical design, API, ADRs, & guides
├── backend/                    # Python 3.12 + FastAPI Application
│   ├── app/
│   │   ├── core/               # Async MongoDB motor client
│   │   ├── middleware/         # Role guard dependency factory
│   │   ├── models/             # Pydantic schemas (User, Task)
│   │   ├── routes/             # API routes (auth, tasks, users)
│   │   ├── utils/              # State machine transition engine
│   │   ├── config.py           # Environment loading
│   │   ├── firebase_auth.py    # Firebase Admin SDK init & token verification
│   │   └── main.py             # FastAPI entry point & CORS
│   ├── tests/                  # Pytest unit & health tests
│   ├── Dockerfile              # Multi-stage Python build
│   └── requirements.txt
├── frontend/                   # React 19 + Vite 8 SPA
│   ├── src/
│   │   ├── components/         # Board, TicketCard, InspectionQueue, etc.
│   │   ├── contexts/           # AuthContext & ToastContext
│   │   ├── pages/              # ManagerDashboard & EmployeeDashboard
│   │   ├── utils/              # Axios instance with Bearer token interceptor
│   │   └── index.css           # Foreman Vanilla CSS design tokens
│   ├── Dockerfile              # Multi-stage Node + Nginx build
│   ├── nginx.conf              # Production Nginx reverse proxy
│   └── package.json
└── k8s/                        # Local minikube Kubernetes manifests
```

---

## 2. State Machine Transition Logic (`backend/app/utils/status_machine.py`)

The state machine is the core domain engine enforcing valid Kanban column transitions and role authorizations:

```python
ALLOWED_TRANSITIONS = {
    "todo": {"in_progress"},
    "in_progress": {"submitted_for_review"},
    "submitted_for_review": {"done", "in_progress"},
    "done": set(),  # Terminal state
}

TRANSITION_ROLES = {
    ("todo", "in_progress"): "employee",
    ("in_progress", "submitted_for_review"): "employee",
    ("submitted_for_review", "done"): "manager",
    ("submitted_for_review", "in_progress"): "manager",
}
```

### Validation Function Signature

```python
def validate_transition(
    current_stage: str,
    new_stage: str,
    user_role: Literal["manager", "employee"]
) -> tuple[bool, str]:
```

---

## 3. Server-Side Role Enforcement (`backend/app/middleware/role_guard.py`)

Role enforcement is handled by the dependency factory `require_role(required_role)`:

```python
@router.post("/tasks", dependencies=[Depends(require_role("manager"))])
async def create_task(...):
    ...
```

### Execution Flow:
1. `verify_firebase_token` extracts the Bearer token from the HTTP `Authorization` header.
2. Firebase Admin SDK verifies token signatures and expiration, returning the decoded `uid`.
3. `require_role` queries MongoDB `users` collection for `firebase_uid`.
4. If `required_role` is specified and user role does not match, a `403 Forbidden` exception is raised.

---

## 4. Frontend Token Injection (`frontend/src/utils/api.js`)

All frontend API calls utilize a centralized Axios instance configured with a request interceptor:

```javascript
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 5. Testing & Linting Commands

### Backend Verification
```bash
cd backend

# Run Ruff linter
ruff check app/

# Run Pytest suite
python -m pytest tests/ -v
```

### Frontend Verification
```bash
cd frontend

# Run ESLint
npm run lint

# Verify Production Build
npm run build
```

---

## 6. Git & Branching Workflow

Follow conventional commit syntax on isolated topic branches:

- **Branch format:** `<category>/<short-description>` (e.g. `feature/websocket-notifications`)
- **Commit format:** `<type>(<scope>): <description>` (e.g. `fix(auth): handle expired token error`)
