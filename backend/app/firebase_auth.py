# backend/app/firebase_auth.py
"""
Firebase Admin SDK initialization and ID token verification.
Supports both file-based (local/dev) and environment variable (cloud) service accounts.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import FIREBASE_SERVICE_ACCOUNT_PATH

# ─── Initialize Firebase Admin SDK ─────────────────────────

def initialize_firebase_admin():
    """
    Initialize Firebase Admin SDK.
    Supports both:
    1. File-based: serviceAccountKey.json (local/dev)
    2. Environment variable: FIREBASE_SERVICE_ACCOUNT_JSON (cloud)
    """
    try:
        # Try environment variable first (cloud deployment)
        sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
            firebase_admin.initialize_app(cred)
            print("✔ Firebase Admin SDK initialized from environment variable")
            return
        
        # Fallback to file-based (local development)
        if os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
            print(f"✔ Firebase Admin SDK initialized from file: {FIREBASE_SERVICE_ACCOUNT_PATH}")
            return
        
        raise FileNotFoundError(f"Service account not found at {FIREBASE_SERVICE_ACCOUNT_PATH}")
    
    except Exception as e:
        print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
        raise

# Initialize only if not already initialized
if not firebase_admin._apps:
    initialize_firebase_admin()

# FastAPI security scheme
bearer_scheme = HTTPBearer()

async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI dependency: verifies Firebase ID token from Authorization header.
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