import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router, load_models_if_needed
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.export_routes import router as export_router
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    print("Initializing SQLite Database...")
    init_db()
    
    # Load models on startup
    print("Pre-loading ML models for optimized performance...")
    load_models_if_needed()
    yield

app = FastAPI(
    title="AI-RADA API",
    description="Backend API for AI-RADA Requirement Analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(export_router, prefix="/api", tags=["export"])
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
