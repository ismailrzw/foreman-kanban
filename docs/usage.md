# Role-Based User & Workflow Guide

> **Foreman Kanban** — User workflows, role permissions, and step-by-step feature walkthroughs.

---

## 1. Overview of Application Roles

Foreman Kanban enforces strict role segregation:

```
+-------------------------------------------------------------------------+
|                              APPLICATION ROLES                          |
+------------------------------------+------------------------------------+
|               MANAGER              |              EMPLOYEE              |
+------------------------------------+------------------------------------+
| • Create work orders               | • View assigned tasks              |
| • Set task complexity (Low/Med/High)| • Transition tasks to "In Progress" |
| • Assign tasks to crew members     | • Submit tasks for inspection      |
| • Access Manager Inspection Queue  | • View rejection feedback inline   |
| • Approve tasks (Stamp "APPROVED") | • Resubmit revised work            |
| • Reject tasks with feedback       |                                    |
| • Edit / Delete work orders        |                                    |
+------------------------------------+------------------------------------+
```

---

## 2. Manager Workflow

### 2.1 Opening a New Work Order

1. Log into your account registered as a **Manager**.
2. Click the **+ New Work Order** button in the top right corner of the Job Board.
3. Fill out the work order fields:
   - **Title:** Descriptive summary (e.g. `Fix Nginx Upstream Timeout`).
   - **Description:** Technical requirements and criteria for sign-off.
   - **Assign to:** Select an employee from the dropdown list.
   - **Complexity:** Low (1 dot), Medium (2 dots), or High (3 dots).
4. Click **Open work order**. The card will appear under the **To Do** column.

### 2.2 Inspecting Submitted Work (Manager Inspection Queue)

When an employee submits a completed job, it enters the **Inspection Queue** (located above the Kanban board columns).

1. Review the task title, assigned employee name, and complexity rating.
2. Choose one of two review actions:
   - **Confirm (Approve):**
     - Click **Confirm**.
     - The task transitions to `done` ("Signed Off"), displaying a green **`APPROVED`** stamp on paper cards.
     - The task is removed from the pending inspection queue.
   - **Send Back (Reject):**
     - Click **Send Back**.
     - An inline rejection panel expands. Enter clear feedback explaining what needs to be corrected.
     - Click **Confirm rejection**.
     - The task moves back to `in_progress` on the board, displaying a red **`SENT BACK`** banner with your feedback text visible on the employee's paper card.

---

## 3. Employee Workflow

### 3.1 Viewing Assigned Work Orders

1. Log into your account registered as an **Employee**.
2. The dashboard automatically filters the Kanban board to display **only tasks assigned to you**.

### 3.2 Starting a Work Order

1. Located a task in the **To Do** column.
2. Click **Start Job**.
3. The task card updates stage to `in_progress` ("In Progress").

### 3.3 Submitting Work for Inspection

1. Once work on a task is completed, navigate to the card in **In Progress**.
2. Click **Submit for Inspection**.
3. The task stage updates to `submitted_for_review` ("For Inspection").
4. The action button changes to `Awaiting Inspection…`, indicating that the task is currently in the Manager's Inspection Queue awaiting sign-off.

### 3.4 Handling Rejections & Resubmitting

1. If a Manager sends back a submission, the card returns to your **In Progress** column with an inline **Rejection Feedback** callout.
2. Read the feedback notes, fix the specified issues, and click **Resubmit for Inspection**.

---

## 4. UI Visual Cue Reference

| Visual Element | Meaning |
|----------------|---------|
| 📌 **Red Pin** | Paper ticket mounting metaphor |
| ●●○ **Complexity Dots** | Complexity rating: 1=Low, 2=Medium, 3=High |
| 🟩 **APPROVED Stamp** | Task confirmed by Manager (Terminal `done` state) |
| 🟥 **SENT BACK Banner** | Task rejected by Manager with feedback required before resubmission |
| 🏷️ **Initials Avatar** | User badge identifying assigned crew member or logged-in user |
