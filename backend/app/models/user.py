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