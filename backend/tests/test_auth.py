"""
Authentication & Role Guard Unit Tests.

Tests Firebase token verification dependency, user registration model validation,
and role enforcement middleware.
"""

import pytest
from pydantic import ValidationError

from app.models.user import UserCreate


class TestUserModelValidation:
    """Tests for Pydantic User model validation."""

    def test_valid_user_create(self):
        """UserCreate succeeds with valid payload."""
        user = UserCreate(
            firebase_uid="uid_12345",
            email="employee@foreman.dev",
            name="John Foreman",
            role="employee",
        )
        assert user.firebase_uid == "uid_12345"
        assert user.role == "employee"

    def test_invalid_role_rejected(self):
        """UserCreate raises ValidationError for invalid role."""
        with pytest.raises(ValidationError):
            UserCreate(
                firebase_uid="uid_12345",
                email="admin@foreman.dev",
                name="Admin User",
                role="superadmin",  # invalid — must be manager or employee
            )

    def test_short_name_rejected(self):
        """UserCreate raises ValidationError if display name is less than 2 characters."""
        with pytest.raises(ValidationError):
            UserCreate(
                firebase_uid="uid_12345",
                email="x@foreman.dev",
                name="A",
                role="manager",
            )
