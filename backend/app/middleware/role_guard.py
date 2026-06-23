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
from app.core.database import get_database


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