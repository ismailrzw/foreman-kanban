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