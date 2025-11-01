"""Main FastAPI application for Märchenweber."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import close_database
from app.routers import adventure

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle (startup/shutdown)."""
    # Startup
    yield
    # Shutdown
    await close_database()


app = FastAPI(
    title="Märchenweber API",
    description="Dynamic LLM storytelling game backend for kids",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for SvelteKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # SvelteKit dev server
        "http://localhost:4173",  # SvelteKit preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

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
