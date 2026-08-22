# Security Architecture & Best Practices

> **Foreman Kanban** — Security controls, authentication mechanics, authorization guards, and secret isolation strategies.

---

## 1. Security Design Principles

Foreman Kanban is designed around defense-in-depth principles:

1. **Zero Client-Side Trust:** All authorization decisions (RBAC) and state machine transition rules are enforced on the backend server.
2. **Delegated Identity Management:** Passwords and authentication credentials are managed exclusively by Firebase Authentication. No sensitive credentials touch application databases.
3. **Cryptographic Token Verification:** Every API mutation verifies Firebase RS256 JWT ID Tokens server-side using the Firebase Admin SDK.
4. **Secret Isolation:** API keys, database credentials, and service account keys are loaded dynamically from environment variables.

---

## 2. Authentication & JWT Token Flow

```
[ Client Browser ] ----(1) Login credentials----> [ Firebase Auth ]
[ Client Browser ] <---(2) Signed ID Token------- [ Firebase Auth ]
        |
        | (3) Request with Authorization: Bearer <token>
        v
[ FastAPI Backend ] ---(4) Verify RS256 Signature--> [ Firebase Admin SDK ]
        |
        | (5) Query user role by firebase_uid
        v
[ MongoDB Atlas ]
```

---

## 3. Server-Side Role-Based Access Control (RBAC)

FastAPI endpoints enforce access control using the `require_role()` dependency:

```python
def require_role(required_role: str = None):
    async def role_dependency(decoded_token: dict = Depends(verify_firebase_token)) -> dict:
        db = get_database()
        user = await db.users.find_one({"firebase_uid": decoded_token["uid"]})
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found.")
        if required_role and user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}."
            )
        return user
    return role_dependency
```

---

## 4. Input Sanitization & Data Validation

- **Pydantic Schemas:** All request payloads are strictly parsed and validated. Input lengths for titles (max 200 chars), descriptions (max 1000 chars), and rejection feedback (max 500 chars) are enforced at the schema layer.
- **MongoDB Injection Defense:** Mongo queries utilize parameterized document filters rather than concatenated string queries, eliminating NoSQL injection vectors.
- **ObjectId Validation:** Path parameter IDs are validated via `ObjectId.is_valid(task_id)` prior to database operations.

---

## 5. Production Nginx Security Headers (`frontend/nginx.conf`)

The production frontend container includes hardened HTTP headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

---

## 6. Vulnerability Reporting

If you discover a potential security vulnerability in Foreman Kanban, please open a private security advisory on GitHub or contact the repository owner.
