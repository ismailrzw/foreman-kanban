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
from app.core.database import get_database

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