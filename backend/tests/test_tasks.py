"""
Task State Machine & Task Logic Unit Tests.

Tests the core domain feature: strict status state machine transition validation
and role-authorized progression (PR review/merge analog).
"""

from app.utils.status_machine import validate_transition


class TestTaskStatusMachine:
    """Unit test suite for status transition validation logic."""

    # ─── Legal Transitions — Authorized Roles ─────────────────

    def test_employee_can_start_todo_task(self):
        """Employee transitions task from 'todo' to 'in_progress'."""
        is_valid, msg = validate_transition("todo", "in_progress", "employee")
        assert is_valid is True
        assert msg == ""

    def test_employee_can_submit_in_progress_task(self):
        """Employee submits task from 'in_progress' to 'submitted_for_review'."""
        is_valid, msg = validate_transition("in_progress", "submitted_for_review", "employee")
        assert is_valid is True
        assert msg == ""

    def test_manager_can_confirm_submitted_task(self):
        """Manager confirms (merges) task from 'submitted_for_review' to 'done'."""
        is_valid, msg = validate_transition("submitted_for_review", "done", "manager")
        assert is_valid is True
        assert msg == ""

    def test_manager_can_reject_submitted_task(self):
        """Manager rejects (requests changes) task from 'submitted_for_review' to 'in_progress'."""
        is_valid, msg = validate_transition("submitted_for_review", "in_progress", "manager")
        assert is_valid is True
        assert msg == ""

    # ─── Illegal Transitions — Stage Skipping ──────────────────

    def test_cannot_skip_to_done_from_todo(self):
        """Cannot jump directly from 'todo' to 'done'."""
        is_valid, msg = validate_transition("todo", "done", "manager")
        assert is_valid is False
        assert "Cannot move task from 'todo' to 'done'" in msg

    def test_cannot_skip_to_submitted_from_todo(self):
        """Cannot jump directly from 'todo' to 'submitted_for_review'."""
        is_valid, msg = validate_transition("todo", "submitted_for_review", "employee")
        assert is_valid is False
        assert "Cannot move task from 'todo' to 'submitted_for_review'" in msg

    def test_cannot_transition_out_of_done(self):
        """'done' is terminal — cannot move to any other stage."""
        for target_stage in ["todo", "in_progress", "submitted_for_review"]:
            is_valid, msg = validate_transition("done", target_stage, "manager")
            assert is_valid is False
            assert "terminal state" in msg

    # ─── Role Authorization Failures ──────────────────────────

    def test_employee_cannot_self_approve(self):
        """Employee cannot confirm a submission to 'done' (self-approval blocked)."""
        is_valid, msg = validate_transition("submitted_for_review", "done", "employee")
        assert is_valid is False
        assert "Only a manager can move a task from 'submitted_for_review' to 'done'" in msg

    def test_employee_cannot_reject_submission(self):
        """Employee cannot send a submission back to 'in_progress'."""
        is_valid, msg = validate_transition("submitted_for_review", "in_progress", "employee")
        assert is_valid is False
        assert "Only a manager" in msg

    def test_manager_cannot_start_employee_task(self):
        """Manager cannot directly transition task from 'todo' to 'in_progress'."""
        is_valid, msg = validate_transition("todo", "in_progress", "manager")
        assert is_valid is False
        assert "Only a employee can move a task from 'todo' to 'in_progress'" in msg
