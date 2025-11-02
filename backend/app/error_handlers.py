"""Global error handlers for FastAPI with structured logging."""

import logging
import traceback
from typing import Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.exceptions import MaerchenweberError

logger = logging.getLogger(__name__)


async def maerchenweber_error_handler(
    request: Request,
    exc: MaerchenweberError
) -> JSONResponse:
    """Handle custom Märchenweber errors with structured response.

    Args:
        request: FastAPI request
        exc: Custom exception

    Returns:
        JSON response with error details
    """
    logger.error(
        f"MaerchenweberError: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )

    # Determine HTTP status code based on error type
    status_code_map = {
        "SESSION_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "SAFETY_VIOLATION": status.HTTP_200_OK,  # Not user's fault, return success with fallback
    }

    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    response_data = exc.to_dict()
    response_data["path"] = request.url.path

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSON response with validation details
    """
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors()
        }
    )

    # Extract field names from errors
    field_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        field_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {"fields": field_errors},
            "user_message": "Ungültige Eingabe. Bitte überprüfe deine Angaben.",
            "path": request.url.path
        }
    )


async def generic_error_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected errors with full context logging.

    Args:
        request: FastAPI request
        exc: Any unhandled exception

    Returns:
        JSON response with sanitized error
    """
    # Log full traceback for debugging
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )

    # Don't expose internal details to users
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {
                "error_type": type(exc).__name__
            },
            "user_message": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.",
            "path": request.url.path
        }
    )


def add_error_handlers(app):
    """Register all error handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(MaerchenweberError, maerchenweber_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    logger.info("Error handlers registered successfully")
