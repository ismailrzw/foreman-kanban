# FOREMAN — KANBAN TASK BOARD

*Team Onboarding & Workflow Guide · Prepared by Ismail (Lead/Integration) · For Ibrahim & Saad*

---

## 1. Where the Project Stands Right Now

I've already done the groundwork so you both can start contributing immediately:

- **Repo created** — full folder structure (`backend/`, `frontend/`, `k8s/`, `.github/workflows/`) is already scaffolded on GitHub.
- **Working MVP pushed to main/develop** — Firebase login/signup, role-based dashboards (Manager vs Employee), and the full task approval workflow (Start → Submit → Confirm/Reject) all work end-to-end.
- **Live cloud deployment is up** — Frontend on Vercel, Backend on Render, Database on MongoDB Atlas. The repo link is already shared with both of you.

Your job now: clone it, run it locally, and build your assigned features on your own branches. I handle all merging and the final cloud redeploy — you focus on writing and testing your code.

---

## 2. Get the Project Running On Your Machine

Run these exactly, in order, in your terminal.

```bash
git clone <repo-link-I-shared>
cd foreman-kanban

# --- Backend (Ibrahim starts here too, to test full stack) ---
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
# Place the .env file and serviceAccountKey.json I send you here
uvicorn app.main:app --reload --port 8000

# --- Frontend (new terminal tab) ---
cd frontend
npm install
# Place the .env file I send you here
npm run dev
```

Open `http://localhost:5173` — you should see the login screen. Sign up once as Manager and once as Employee (use a private/incognito window for the second) to see both dashboards.

> **Never commit `.env` or `serviceAccountKey.json`** — they're already in `.gitignore`. I'll send them to you privately, not over GitHub or group chat.

---

## 3. How We Work Together — Branch & PR Rules

| Branch | Who Pushes To It | Purpose |
|---|---|---|
| `main` | Nobody directly | Live/production code — only updated by Ismail merging from develop |
| `develop` | Nobody directly | Integration branch — where your finished features land first |
| `feature/backend/*` | Ibrahim | Every backend feature gets its own branch off develop |
| `feature/frontend/*` | Saad | Every frontend feature gets its own branch off develop |

- **The rule** — Only Ismail merges. You write code, push your branch, and open a Pull Request (PR). I review it and merge it myself. You never click "Merge" yourselves.
- **You still do everything else yourselves** — building Docker images, running containers, deploying to your own local Kubernetes (minikube), and fixing your own bugs. I'm only the gatekeeper for what goes into develop/main, not a bottleneck for your day-to-day work.
- **Commit message format** — `"feat(backend): short description"` or `"feat(frontend): short description"`. Small, frequent commits are better than one giant commit.

---

## 4. Full Project Flow — Step by Step, Who Does What

This section walks through the entire rest of the project from today until the final demo — what happens first, what happens in parallel, which files each of you touches, and what "done" looks like for every increment. Read this once fully before you write any code.

### 4.1 The Big Picture

Phase 0 (bare repo) and Phase 1 (working MVP — auth, roles, the full task approval flow) are both finished and already merged into main/develop. From here, the project moves into Phase 6: five independent feature increments each, built in parallel by Ibrahim and Saad on separate branches, reviewed and merged one at a time by Ismail. Nothing either of you builds touches the other's files, so you can both work at the same time without conflicts.

- **Ibrahim** works entirely inside `backend/` — Python, FastAPI, MongoDB. He never needs to open `frontend/`.
- **Saad** works entirely inside `frontend/` — React components, pages, and styling. He never needs to open `backend/`.
- Each feature is self-contained: one branch, a small number of files, one Pull Request, one review, one merge. You do not wait for the other person to finish their feature before starting yours — they are independent.
- After a feature is merged into develop, pull develop again before starting the next one, since later features sometimes build on top of earlier ones (e.g. the audit trail logs actions defined in earlier features).

**Recommended order for both of you:** build features 1 → 5 in numeric order, since later ones occasionally reference fields or endpoints introduced in earlier ones (this is called out per-feature below).

---

### 4.2 Ibrahim's Track — Backend (5 Increments)

*Everything below happens inside the `backend/` folder. After each feature, run the local server, hit the new endpoint(s) with curl or the FastAPI docs page (`http://localhost:8000/docs`), confirm the behavior, then build and run the Docker image before opening the PR.*

#### Increment B1 — Rejection History & Revision Tracking

*Branch: `feature/backend/rejection-history`*

Right now, when a Manager rejects a task, the old feedback gets overwritten the next time it's rejected — there's no record of how many times a task bounced back or what was said each time. This increment adds a permanent, append-only history of every rejection, the same way a GitHub PR keeps every round of review comments instead of replacing them.

- **`backend/app/models/task.py`** — add a new `RevisionEntry` model (`revision_number`, `rejected_at`, `feedback`, `rejected_by`) and add `revision_history` (a list of `RevisionEntry`) plus `revision_count` to `TaskResponse`.
- **`backend/app/routes/task_routes.py`** — inside `review_task()`, when `action == "reject"`: push a new `RevisionEntry` onto the task's `revision_history` array in MongoDB using `$push`, and increment `revision_count` using `$inc`, instead of just overwriting `rejection_feedback`.
- **`backend/app/routes/task_routes.py`** — add a brand-new endpoint, `GET /api/tasks/{task_id}/history`, that returns the task's `id`, `revision_count`, and the full list of revisions in order.
- **`backend/tests/test_tasks.py`** — add a test that rejects the same task twice and asserts `revision_count` is 2 and both feedback messages are present in the history.

**Done when:** rejecting a task three times produces three entries in `revision_history`, the count matches, and `GET /api/tasks/{id}/history` returns them in order with no missing fields.

---

#### Increment B2 — Complexity-Weighted Workload Dashboard

*Branch: `feature/backend/workload-dashboard`*

Managers currently have no way to see who is overloaded. This increment adds an analytics endpoint that sums each employee's tasks weighted by complexity (Low=1, Medium=2, High=3), broken down by stage, so a Manager can see at a glance who has too much on their plate before assigning anything new.

- **`backend/app/routes/analytics_routes.py`** — new file. Create one Manager-only endpoint, `GET /api/analytics/workload`, that loops through all employees and, for each one, counts their tasks and sums complexity values, both overall and split by stage (`todo` / `in_progress` / `submitted_for_review` / `done`).
- **`backend/app/main.py`** — import and register the new `analytics_router` the same way `auth_router`, `task_router`, and `user_router` are registered.
- **`backend/tests/test_tasks.py`** — add a test with a known set of tasks (e.g. 2 Low + 1 High for one employee) and assert the returned `weighted_load` matches the expected sum.

**Done when:** the endpoint returns one entry per employee — including employees with zero tasks, showing all zeros rather than being omitted — and the numbers match a manual calculation.

---

#### Increment B3 — Deadlines & Overdue Flagging

*Branch: `feature/backend/deadlines`*

Tasks currently have no concept of time pressure. This increment lets a Manager optionally set a deadline when creating a task, and adds a way to surface anything that's now late.

- **`backend/app/models/task.py`** — add an optional `deadline` field (`datetime`) to `TaskCreate`, `TaskUpdate`, and `TaskResponse`, and add a computed `is_overdue` boolean field to `TaskResponse`.
- **`backend/app/routes/task_routes.py`** — in `list_tasks()` and anywhere a task is converted to a response, compute `is_overdue` by comparing `deadline` to the current time, but only for tasks not yet in the `done` stage.
- **`backend/app/routes/task_routes.py`** — add a new Manager-only endpoint, `GET /api/tasks/overdue`, that filters and returns only tasks where `is_overdue` is true.
- **`backend/tests/test_tasks.py`** — add a test that creates a task with a deadline in the past and asserts `is_overdue` is true, and one with a deadline in the future asserting it's false.

**Done when:** a task created with no deadline never shows as overdue, a task past its deadline shows `is_overdue: true` everywhere it appears, and `/api/tasks/overdue` returns exactly the late ones.

---

#### Increment B4 — Full Audit Trail

*Branch: `feature/backend/audit-trail`*

This is the accountability layer — every single action taken on a task (created, started, submitted, confirmed, rejected, updated, deleted) gets permanently logged with who did it, their role, and what changed. This builds on B1's revision history but covers every action type, not just rejections.

- **`backend/app/models/audit.py`** — new file. Define an `AuditLogEntry` model: `task_id`, `action`, `performed_by`, `performed_by_name`, `performed_by_role`, `previous_stage`, `new_stage`, `details`, `timestamp`.
- **`backend/app/routes/task_routes.py`** — write one small helper function, e.g. `write_audit_log(...)`, that inserts an `AuditLogEntry` into a new `audit_logs` MongoDB collection. Call this helper from inside `create_task`, `start_task`, `submit_for_review`, `review_task`, `update_task`, and `delete_task` — every place the task's state changes.
- **`backend/app/routes/audit_routes.py`** — new file. Add `GET /api/tasks/{task_id}/audit` (Manager only — full trail for one task) and `GET /api/audit/recent` (Manager only — last 50 entries across all tasks system-wide).
- **`backend/app/main.py`** — register the new `audit_router`.
- **`backend/tests/test_tasks.py`** — verify that creating, starting, and submitting one task produces three matching audit log entries in the correct order.

**Done when:** every action type appears correctly in the per-task trail, and `/api/audit/recent` shows activity across multiple tasks sorted by most recent first.

---

#### Increment B5 — Manager Performance Analytics

*Branch: `feature/backend/manager-analytics`*

The final backend increment ties B2 and B4 together into a real reporting view: completion rate, average time from creation to done, rejection rate, and complexity distribution, both overall and per employee.

- **`backend/app/routes/analytics_routes.py`** — add a second endpoint, `GET /api/analytics/metrics`, that calculates: `total_tasks`, `completed`, `completion_rate` (completed/total), `avg_completion_time_hours` (using `created_at` and the timestamp the task last became done), and `rejection_rate` (using `revision_count` or audit log rejection actions from B1/B4). Compute the same set per employee under a `per_employee` array, including a `complexity_distribution` count.
- **`backend/tests/test_tasks.py`** — test with a fixed set of completed/rejected/pending tasks and assert the rates and averages match hand-calculated expected values. Specifically test the case where an employee has zero completed tasks, to make sure you don't divide by zero.

**Done when:** the metrics object returns sensible values for both a busy employee and a brand-new employee with no history, and the numbers are internally consistent with what B2's workload endpoint reports.

---

### 4.3 Saad's Track — Frontend (5 Increments)

*Everything below happens inside the `frontend/` folder. After each feature, test it by clicking through the UI as both a Manager and an Employee account in the browser, then build and run the frontend Docker image before opening the PR.*

#### Increment F1 — Enhanced Manager Review Queue

*Branch: `feature/frontend/review-queue`*

The Manager's current Inspection Queue just lists pending tasks with Confirm/Send Back buttons. This increment turns it into a real review inbox: filterable by employee and complexity, with an expandable detail panel per task, and a batch "Confirm All Visible" action.

- **`frontend/src/components/InspectionQueue.jsx`** — add `filterEmployee` and `filterComplexity` state, render two dropdowns above the queue list, and filter the tasks array before rendering based on the selected values.
- **`frontend/src/components/InspectionQueue.jsx`** — add a click handler on each queue item that expands/collapses a detail section showing the full description, the assignee's name, and (once B1/B4 are merged on the backend) the revision history for that task.
- **`frontend/src/components/InspectionQueue.jsx`** — add a "Confirm All" button that loops through the currently filtered/visible tasks and calls the confirm action on each one.
- **`frontend/src/index.css`** — add styles for the filter bar, the expanded detail panel, and the batch-action button, matching the existing Foreman panel/hairline/amber-accent look.

**Done when:** filtering by a specific employee shows only their submissions, filtering by complexity narrows the list correctly, clicking a task expands details without breaking the rest of the layout, and Confirm All correctly confirms every visible task.

---

#### Increment F2 — Employee Workload View

*Branch: `feature/frontend/workload-view`*

Employees currently only see their board grouped by stage. This increment adds an alternate view grouped by complexity instead, with progress bars, so an employee can see how much Low/Medium/High work they have outstanding at a glance.

- **`frontend/src/components/WorkloadView.jsx`** — new file. Group the employee's tasks into three buckets (complexity 1, 2, 3). For each bucket render a header with the label (Low/Medium/High) and count, a progress bar showing the percentage of that bucket's tasks that are in the `done` stage, and the existing `TicketCard` components for each task in that bucket.
- **`frontend/src/pages/EmployeeDashboard.jsx`** — add a small toggle ("Board View" / "Workload View") above the board, and conditionally render either the existing board or the new `WorkloadView` component based on which is selected.
- **`frontend/src/index.css`** — add `.workload-view`, `.workload-group`, and `.progress-bar` styles.

**Done when:** switching the toggle correctly swaps between the two layouts without losing data, and the progress bars accurately reflect the done/total ratio for each complexity bucket.

---

#### Increment F3 — Drag-and-Drop Board

*Branch: `feature/frontend/drag-drop`*

Currently, moving a task forward requires clicking a button on the card. This increment lets users drag a card between columns directly — but only when the backend's status machine would actually allow that move for their role, so dragging a card somewhere illegal must visibly fail, not silently succeed.

- **`frontend/src/components/TicketCard.jsx`** — make the outer ticket div draggable (HTML5 drag-and-drop), storing the task's `id` and current stage in the drag event's `dataTransfer` on `dragstart`, and reducing opacity while dragging.
- **`frontend/src/components/BoardColumn.jsx`** — add `onDragOver`, `onDragLeave`, and `onDrop` handlers to the column body. On drop, read the task id and origin stage from `dataTransfer`, and call an `onDrop(taskId, fromStage, toStage)` callback passed down from the parent page rather than calling the API directly from inside the column.
- **`frontend/src/pages/ManagerDashboard.jsx`** and **`frontend/src/pages/EmployeeDashboard.jsx`** — implement the `onDrop` callback: call the matching existing API action (`/start`, `/submit`, or `/review`) based on the `fromStage`/`toStage` pair, show a success toast on success, and show an error toast with the backend's message if the status machine rejects the move.
- **`frontend/src/index.css`** — add a `.drag-over` style (amber glow) for valid drop targets while dragging, and ideally a way to visually indicate invalid targets.

**Done when:** legal drags (e.g. an employee dragging their own todo card into in_progress) work and update the board; illegal drags (e.g. dragging straight into done) are rejected by the backend and show a clear error toast instead of silently failing or crashing.

---

#### Increment F4 — Dark/Light Theme Toggle

*Branch: `feature/frontend/dark-mode`*

The app currently only has the dark Foreman theme. This increment adds a full light theme alternative and a toggle to switch between them, with the choice remembered between visits.

- **`frontend/src/utils/theme.js`** — new file. Add `getStoredTheme()`, `setStoredTheme(theme)`, and `initTheme()` helpers that read/write the chosen theme to `localStorage` and set a `data-theme` attribute on the root `<html>` element.
- **`frontend/src/index.css`** — define a full second set of color tokens under a `[data-theme="light"]` selector, redesigning every CSS variable (background, panel, paper, ink, text colors) for a light industrial look that still fits the Foreman aesthetic, and add smooth transition rules so switching themes isn't jarring.
- **`frontend/src/components/Topbar.jsx`** — add a sun/moon toggle button that calls `setStoredTheme()` with the opposite of the current theme.
- **`frontend/src/App.jsx`** — call `initTheme()` once when the app first loads, before anything renders.

**Done when:** every screen — auth, both dashboards, modals, the toast, the ticket cards — looks correct and readable in both themes, and the chosen theme persists after a full page refresh.

---

#### Increment F5 — Notification Bell

*Branch: `feature/frontend/notifications`*

The final frontend increment adds a notification system so users don't have to keep refreshing to know something changed — new assignments for employees, new submissions awaiting review for managers, and confirm/reject outcomes for employees.

- **`frontend/src/components/NotificationBell.jsx`** — new file. Poll `GET /api/tasks` every 10 seconds using a timer, and on each poll compare the new task list against the previous one (kept in a ref) to detect: a new task assigned to the current user, a task that moved into `done` (was `submitted_for_review` — meaning it was approved), a task that moved back into `in_progress` with `is_rejected` true (meaning it was sent back), and — for managers only — a task that newly entered `submitted_for_review`.
- **`frontend/src/components/NotificationBell.jsx`** — store detected events as notification objects (`{ id, message, time, read }`) in state, render a bell icon with an unread-count badge, and a dropdown panel listing them with a "Mark all as read" action.
- **`frontend/src/components/Topbar.jsx`** — render `<NotificationBell />` next to the existing logout icon button.
- **`frontend/src/index.css`** — add styles for the badge, the dropdown panel, and individual notification rows, matching the existing Foreman component styling.

**Done when:** assigning a task to an employee produces a notification in their bell within 10 seconds, and approving/rejecting a submission produces the matching notification for the employee, without duplicate notifications appearing on every poll cycle.

---

## 5. Daily Git Workflow — Copy This Every Time

```bash
git checkout develop
git pull origin develop
git checkout -b feature/backend/your-feature-name      # or feature/frontend/...

# ... write code, test locally, build & run your Docker container ...

git add -A
git commit -m "feat(backend): add rejection history tracking"
git push origin feature/backend/your-feature-name

# Open a Pull Request on GitHub: base = develop, compare = your branch
# Fill in the PR template, request review from Ismail
# If CI fails or I leave review comments: fix, commit, push again — same branch

# Once I merge it:
git checkout develop
git pull origin develop
git branch -d feature/backend/your-feature-name
```

---

## 6. Docker & Kubernetes — You Each Own Your Service

- **Before opening any PR** — build your own Docker image, run it standalone, and confirm it works. Then run the full stack with `docker compose up --build` from the repo root.
- **Ibrahim** — `docker build -t foreman-backend:dev ./backend`, test with curl against `/api/health` and your new endpoints.
- **Saad** — `docker build -t foreman-frontend:dev ./frontend`, open it in the browser on `localhost:3000`, click through both roles.
- **Local Kubernetes** — once your feature works in Docker, deploy it to your own minikube cluster (`kubectl apply -f k8s/`), scale your deployment, and intentionally break something (wrong image tag, bad env var) once, then fix it. This is the troubleshooting practice — do it at least once before the demo.

---

## 7. The PR Review Process (What Happens After You Push)

1. You open a PR from your feature branch into `develop`, using the PR template.
2. GitHub Actions CI runs automatically — lint, tests, Docker build. If it's red, fix it before I review.
3. I review your code and either approve & merge, or leave comments asking for changes.
4. If changes are requested, push new commits to the same branch — the PR updates automatically, no need to reopen.
5. Once merged into `develop`, I periodically batch-merge `develop` into `main`, which triggers the cloud redeploy automatically.

---

## 8. How This Wraps Up (My Side)

Once both of you have all 5 features merged into develop, here's what I do to close out the project:

1. **Final integration pass** — merge `develop` into `main`, confirm CI/CD pipeline pushes new Docker images and triggers Render + Vercel redeploys.
2. **Full regression test** on the live cloud URL — both roles, all 10 new features, end-to-end task flow (assign → start → submit → confirm/reject).
3. **Collect demo evidence** — screenshots of merged PRs, green CI/CD runs, Kubernetes pods running locally for each of us, and the live public URLs.
4. **Run the final demo together** — I'll walk through the Manager flow, Ibrahim demos his backend features + Docker/K8s work, Saad demos his frontend features + Docker/K8s work.
5. **Submit** the repo link, live URLs, and our individual DevOps logs (the commands and screenshots each of us collected while building, breaking, and fixing things).

---

*Questions about your specific tasks? Check the full Phase-by-phase spec in the README first — it has the exact code and the one piece left for you to write. If something's still unclear, ping me directly.*
