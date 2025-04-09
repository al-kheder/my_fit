import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware
from app.db.database import database
from app.routers.workouts import router as workout_router
from app.app_configs.logging_configuration import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # configure logging will run before the app start
    configure_logging()
    """Lifespan context manager for the FastAPI application."""
    # Startup: Connect to database
    await database.connect()
    logger.info("Connected to the databases...")
    yield
    # Shutdown: Disconnect from database
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(workout_router,tags=["workouts"])

@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


