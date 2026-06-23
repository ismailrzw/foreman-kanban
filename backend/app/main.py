"""
FastAPI application entry point.
Configures CORS, connects to MongoDB, and registers all route modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import FRONTEND_URL
from app.core.database import connect_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager — connects to MongoDB on startup,
    disconnects on shutdown.
    """
    await connect_db()
    yield
    await close_db()


# ─── FastAPI App ──────────────────────────────────────────────

app = FastAPI(
    title="Foreman API",
    description="Collaborative Kanban Task Board — Role-Based Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routes ─────────────────────────────────────────
# Import routes AFTER app creation to avoid circular imports

from app.routes.auth_routes import router as auth_router
from app.routes.task_routes import router as task_router
from app.routes.user_routes import router as user_router
from app.routes.audit_routes import router as audit_router
from app.routes.analytics_routes import router as analytics_router

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)
app.include_router(audit_router)
app.include_router(analytics_router)




@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker/K8s probes."""
    return {"status": "healthy", "service": "foreman-backend"} # Test CI
