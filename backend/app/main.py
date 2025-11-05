"""Main FastAPI application for Märchenweber."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger
from app.database import close_database, ensure_indexes
from app.routers import adventure
from app.error_handlers import add_error_handlers


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key for production deployments."""

    async def dispatch(self, request: Request, call_next):
        # Only check API key if API_KEY env var is set (production mode)
        api_key = os.getenv("API_KEY")

        if api_key:
            # In production, validate API key for /adventure routes
            if request.url.path.startswith("/adventure"):
                request_api_key = request.headers.get("X-API-Key")

                if not request_api_key or request_api_key != api_key:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid or missing API key"}
                    )

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle (startup/shutdown)."""
    # Startup
    logger.info("Starting up Märchenweber API...")
    await ensure_indexes()
    logger.info("Startup complete")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_database()


app = FastAPI(
    title="Märchenweber API",
    description="Dynamic LLM storytelling game backend for kids",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for SvelteKit frontend
# Get additional allowed origins from environment variable (comma-separated)
allowed_origins = [
    "http://localhost:5173",  # SvelteKit dev server
    "http://localhost:4173",  # SvelteKit preview
]

# Add production origins if specified
production_origins = os.getenv("ALLOWED_ORIGINS", "")
if production_origins:
    allowed_origins.extend([origin.strip() for origin in production_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key validation middleware
app.add_middleware(APIKeyMiddleware)

# Register error handlers
add_error_handlers(app)

# Include routers
app.include_router(adventure.router, prefix="/adventure", tags=["adventure"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Märchenweber API is running", "status": "healthy"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "maerchenweber-api",
        "version": "1.0.0"
    }
