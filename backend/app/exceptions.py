"""Custom exceptions for Märchenweber with structured error handling."""

from typing import Optional, Dict, Any


class MaerchenweberError(Exception):
    """Base exception for all Märchenweber errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        """Initialize error.

        Args:
            message: Technical error message (for logs)
            error_code: Machine-readable error code
            details: Additional context for debugging
            user_message: User-friendly German message
            retry_after: Seconds to wait before retrying (if applicable)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        self.retry_after = retry_after

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "user_message": self.user_message,
            "retry_after": self.retry_after
        }


class LLMError(MaerchenweberError):
    """Error during LLM API call."""

    def __init__(
        self,
        message: str,
        model: str,
        prompt_length: Optional[int] = None,
        original_error: Optional[Exception] = None,
        retry_after: Optional[int] = None
    ):
        details = {
            "model": model,
            "prompt_length": prompt_length,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            details=details,
            user_message="Die KI-Generierung hat nicht funktioniert. Bitte versuche es erneut.",
            retry_after=retry_after
        )


class ImageGenerationError(MaerchenweberError):
    """Error during image generation."""

    def __init__(
        self,
        message: str,
        session_id: str,
        round_number: int,
        original_error: Optional[Exception] = None
    ):
        details = {
            "session_id": session_id,
            "round": round_number,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            error_code="IMAGE_GENERATION_ERROR",
            details=details,
            user_message="Das Bild konnte nicht erstellt werden. Die Geschichte geht weiter!",
            retry_after=5
        )


class ValidationError(MaerchenweberError):
    """Error during input validation."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {
            "field": field,
            "invalid_value": str(value) if value else None
        }
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            user_message="Ungültige Eingabe. Bitte überprüfe deine Angaben."
        )


class SessionNotFoundError(MaerchenweberError):
    """Session not found in database."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id},
            user_message="Deine Geschichte wurde nicht gefunden. Bitte starte ein neues Abenteuer."
        )


class SafetyViolationError(MaerchenweberError):
    """Content failed safety check."""

    def __init__(self, content_preview: str):
        super().__init__(
            message="Content failed safety validation",
            error_code="SAFETY_VIOLATION",
            details={"content_preview": content_preview[:100]},
            user_message="Oh, lass uns eine andere Geschichte erzählen!"
        )


class RateLimitError(MaerchenweberError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after},
            user_message=f"Zu viele Anfragen. Bitte warte {retry_after} Sekunden.",
            retry_after=retry_after
        )


class DatabaseError(MaerchenweberError):
    """Database operation failed."""

    def __init__(
        self,
        message: str,
        operation: str,
        collection: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {
            "operation": operation,
            "collection": collection,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            user_message="Datenbankfehler. Bitte versuche es erneut."
        )
