import logging
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
# Ensure all models are loaded so Base.metadata knows about them
import models  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bank_system")

app = FastAPI(
    title="Apex Bank Account & Transaction Management System",
    description=(
        "Production-minded Bank Account and Transaction Management API.\n\n"
        "### Key Architecture Features:\n"
        "- **ACID Atomicity & Consistency**: Single database transaction for balance updates and transaction records.\n"
        "- **Pessimistic Row Locking (`SELECT ... FOR UPDATE`)**: Protects accounts from overdrafts during concurrent transactions.\n"
        "- **Deadlock-Free Concurrent Transfers**: Account rows are deterministically locked in ascending UUID order.\n"
        "- **Transaction Immutability**: Append-only transactional history with zero update or delete endpoints.\n"
        "- **Arbitrary Precision Arithmetic**: 100% `Decimal` calculations; floats are forbidden for financial computations.\n"
        "- **PostgreSQL on Neon Cloud**: Native integration using Psycopg 3 driver with serverless connection pooling.\n"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.APP_ENV,
    }


@app.on_event("startup")
def on_startup():
    logger.info("Initializing Apex Bank backend application...")
    # Optional auto-creation of tables if migrations have not been applied yet
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified successfully.")
    except Exception as e:
        logger.error(f"Error checking database tables: {e}")
