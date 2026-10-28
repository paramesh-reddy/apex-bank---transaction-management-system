import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from api.v1.router import api_router
from core.database import engine, Base
import models  # noqa: F401  # registers tables on Base.metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bank_system")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting %s", settings.PROJECT_NAME)
    try:
        # Alembic is the source of truth. create_all only fills in if
        # someone starts the API before running migrations.
        Base.metadata.create_all(bind=engine)
        logger.info("Database connection ok")
    except Exception:
        logger.exception("Could not reach the database on startup")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Apex Bank Account & Transaction Management System",
    description="Account, transaction, and transfer API. Balances use Decimal and row locks.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for consistent JSON error responses
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.APP_ENV,
    }
