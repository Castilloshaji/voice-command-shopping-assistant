from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import health

# Create database tables on startup (Phase 1 SQLite baseline)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include baseline routers
app.include_router(health.router)
app.include_router(health.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Voice Command Shopping Assistant API",
        "docs": "/docs",
        "health": "/health"
    }
