import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware
from app.db.database import database
from app.routers.workouts import router as workout_router
from app.routers.user import router as user_router
from app.routers.goals import router as goal_router
from app.routers.progress import router as summary_router

from app.app_configs.logging_configuration import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    """Lifespan context manager for the FastAPI application."""
    await database.connect()
    logger.info("Connected to the databases...")
    yield
    await database.disconnect()

app = FastAPI(
    title="My Fit API",
    description="A comprehensive fitness tracking REST API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CorrelationIdMiddleware)

# Health check endpoints for Render
@app.get("/")
async def root():
    return {
        "message": "Welcome to My Fit API", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}

# Include routers
app.include_router(workout_router, tags=["workouts"])
app.include_router(user_router, tags=["user"])
app.include_router(goal_router, tags=["goals"])
app.include_router(summary_router, tags=["summary"])

@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)