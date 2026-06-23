import os
import json
import sys
from unittest.mock import MagicMock
import firebase_admin
import firebase_admin.credentials

# Mock Firebase initialization before importing app modules
firebase_admin.credentials.Certificate = MagicMock()
firebase_admin.initialize_app = MagicMock()

# Set mock Firebase credentials
os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"] = json.dumps({
    "type": "service_account",
    "project_id": "mock-project"
})

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
import app.core.database as app_db
from app.main import app
from app.firebase_auth import verify_firebase_token




# ─── Mock Database Client ─────────────────────────────────────

class MockCursor:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def sort(self, field, direction=-1):
        if field == "created_at":
            self.data.sort(key=lambda x: x.get("created_at"), reverse=(direction == -1))
        elif field == "timestamp":
            self.data.sort(key=lambda x: x.get("timestamp"), reverse=(direction == -1))
        return self

    def limit(self, limit_num):
        self.data = self.data[:limit_num]
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        val = self.data[self.index]
        self.index += 1
        return val


class MockCollection:
    def __init__(self, name, db):
        self.name = name
        self.db = db

    async def find_one(self, query):
        results = self._filter(query)
        return dict(results[0]) if results else None

    def find(self, query=None):
        query = query or {}
        results = self._filter(query)
        return MockCursor(results)

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.db.data[self.name].append(doc)
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc["_id"])

    async def update_one(self, query, update_op):
        results = self._filter(query)
        if not results:
            class UpdateResult:
                modified_count = 0
            return UpdateResult()
        
        doc = results[0]
        if "$set" in update_op:
            for k, v in update_op["$set"].items():
                doc[k] = v
        if "$push" in update_op:
            for k, v in update_op["$push"].items():
                if k not in doc:
                    doc[k] = []
                doc[k].append(v)
        if "$inc" in update_op:
            for k, v in update_op["$inc"].items():
                doc[k] = doc.get(k, 0) + v
                
        class UpdateResult:
            modified_count = 1
        return UpdateResult()

    async def delete_one(self, query):
        results = self._filter(query)
        if not results:
            class DeleteResult:
                deleted_count = 0
            return DeleteResult()
        
        self.db.data[self.name].remove(results[0])
        class DeleteResult:
            deleted_count = 1
        return DeleteResult()

    def _filter(self, query):
        matched = []
        for doc in self.db.data[self.name]:
            match = True
            for k, v in query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v) and doc.get("_id") != v:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                matched.append(doc)
        return matched

    async def aggregate(self, pipeline):
        # Implement dynamic python-based aggregation matching our endpoints
        # Workload aggregation (Feature B2)
        if self.name == "tasks" and len(pipeline) > 0 and "$facet" not in str(pipeline):
            # For simplicity, we can implement custom handlers based on pipeline steps
            pass

        # Since we'll write the aggregate query in analytics_routes.py,
        # we can provide custom calculation logic if called
        return MockCursor([])


class MockDatabase:
    def __init__(self):
        self.data = {
            "users": [],
            "tasks": [],
            "audit_logs": []
        }
        self.users = MockCollection("users", self)
        self.tasks = MockCollection("tasks", self)
        self.audit_logs = MockCollection("audit_logs", self)

    def get_default_database(self):
        return self


# ─── Auth Mocking ─────────────────────────────────────────────

bearer_scheme = HTTPBearer()

async def mock_verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    token = credentials.credentials
    if token == "manager-token":
        return {"uid": "uid-mgr", "email": "mgr@test.com"}
    elif token == "employee-token":
        return {"uid": "uid-emp", "email": "emp@test.com"}
    elif token.startswith("token-"):
        uid = token.split("token-")[1]
        return {"uid": uid, "email": f"{uid}@test.com"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─── Pytest Fixtures ───────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_mocks():
    # Setup mock database
    mock_db = MockDatabase()
    app_db._database = mock_db

    # Insert default users
    mock_db.data["users"].extend([
        {
            "_id": ObjectId(),
            "firebase_uid": "uid-mgr",
            "email": "mgr@test.com",
            "name": "Test Manager",
            "role": "manager"
        },
        {
            "_id": ObjectId(),
            "firebase_uid": "uid-emp",
            "email": "emp@test.com",
            "name": "Test Employee",
            "role": "employee"
        }
    ])

    # Override dependencies
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    yield mock_db

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
