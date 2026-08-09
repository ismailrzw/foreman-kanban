import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import FIREBASE_SERVICE_ACCOUNT_PATH

def initialize_firebase_admin():
    try:
        sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
            firebase_admin.initialize_app(cred)
            return
        if os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
            return
        raise FileNotFoundError(f"Service account not found at {FIREBASE_SERVICE_ACCOUNT_PATH}")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin SDK: {e!s}")
        raise

if not firebase_admin._apps:
    initialize_firebase_admin()

bearer_scheme = HTTPBearer()

async def verify_firebase_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = None,
) -> dict:
    if credentials is None:
        credentials = await bearer_scheme.__call__(request)

    token = credentials.credentials
    try:
        return auth.verify_id_token(token)
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase ID token.")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firebase ID token has expired. Please re-authenticate.")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firebase ID token has been revoked.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not verify credentials: {e!s}")