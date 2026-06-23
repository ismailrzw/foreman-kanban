# backend/app/config.py
"""
Configuration module — loads environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ─── MongoDB ─────────────────────────────────────────────────

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("⚠️  WARNING: MONGO_URI not set in environment!")
    print("   Using default: mongodb://localhost:27017/foreman_db")
    MONGO_URI = "mongodb://localhost:27017/foreman_db"

# ─── Firebase Service Account ──────────────────────────────

FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_PATH", 
    "./serviceAccountKey.json"
)

# ─── CORS ────────────────────────────────────────────────────

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# ─── Environment ────────────────────────────────────────────

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ─── Validation ─────────────────────────────────────────────

def validate_config():
    """Check if all required config is present."""
    issues = []
    
    if not os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON") and not os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
        issues.append(f"Firebase service account file not found at: {FIREBASE_SERVICE_ACCOUNT_PATH}")
    
    if issues:
        print("⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("   The app may not work correctly.")
        return False
    return True

# Run validation on import
validate_config()