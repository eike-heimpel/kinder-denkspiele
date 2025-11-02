# Error Handling Guide

**Last Updated:** 2025-11-02
**Purpose:** Document error handling architecture and best practices for Märchenweber API

---

## Overview

The Märchenweber API uses a structured error handling system with:
- **Custom exception hierarchy** for semantic error types
- **Global error handlers** for consistent responses
- **Structured logging** with context
- **User-friendly messages** in German
- **Graceful degradation** for non-critical failures

---

## Exception Hierarchy

### Base Exception: `MaerchenweberError`

**Location:** `backend/app/exceptions.py`

All custom exceptions inherit from `MaerchenweberError`:

```python
class MaerchenweberError(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message              # Technical error message (logs)
        self.error_code = error_code        # Machine-readable error code
        self.details = details or {}        # Additional context
        self.user_message = user_message    # User-friendly German message
        self.retry_after = retry_after      # Retry delay in seconds
```

### Specialized Exceptions

| Exception | Error Code | Use Case | HTTP Status |
|-----------|-----------|----------|-------------|
| `ValidationError` | VALIDATION_ERROR | Invalid input data | 422 |
| `SessionNotFoundError` | SESSION_NOT_FOUND | Game session not found | 404 |
| `LLMError` | LLM_ERROR | LLM API failures | 500 |
| `ImageGenerationError` | IMAGE_GENERATION_ERROR | Image generation failures | 500 |
| `SafetyViolationError` | SAFETY_VIOLATION | Content safety violations | 200* |
| `RateLimitError` | RATE_LIMIT_EXCEEDED | API rate limits hit | 429 |
| `DatabaseError` | DATABASE_ERROR | MongoDB operation failures | 500 |

*Safety violations return 200 with fallback content (not user's fault)

---

## Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": "Technical error message",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {
    "field": "choice_text",
    "value": 501,
    "additional_context": "..."
  },
  "user_message": "Benutzerfreundliche deutsche Nachricht",
  "retry_after": 5,
  "path": "/adventure/turn"
}
```

**Fields:**
- `error` - Technical message (for developers/logs)
- `error_code` - Machine-readable code (for frontend logic)
- `details` - Additional context (varies by error type)
- `user_message` - User-friendly German message (display to user)
- `retry_after` - Retry delay in seconds (optional)
- `path` - Request path that caused the error

---

## Raising Exceptions

### Example 1: Validation Error

```python
from app.exceptions import ValidationError

if not request.choice_text or len(request.choice_text.strip()) < 1:
    raise ValidationError(
        message="Choice text cannot be empty",
        field="choice_text",
        value=request.choice_text
    )

if len(request.choice_text) > 500:
    raise ValidationError(
        message="Choice text too long (max 500 characters)",
        field="choice_text",
        value=len(request.choice_text)
    )
```

### Example 2: Session Not Found

```python
from app.exceptions import SessionNotFoundError

session = await collection.find_one({"_id": ObjectId(session_id)})
if not session:
    raise SessionNotFoundError(session_id)
```

### Example 3: LLM Error

```python
from app.exceptions import LLMError

try:
    result = await self.llm.generate_text(...)
except Exception as e:
    raise LLMError(
        message=f"Failed to generate story: {str(e)}",
        model=model,
        prompt_length=len(prompt),
        original_error=e
    )
```

### Example 4: Image Generation Error

```python
from app.exceptions import ImageGenerationError

try:
    image_url = await self.llm.generate_image(...)
except Exception as e:
    raise ImageGenerationError(
        message=f"Image generation failed: {str(e)}",
        session_id=session_id,
        round_number=current_round,
        original_error=e
    )
```

---

## Error Handlers

**Location:** `backend/app/error_handlers.py`

Three global error handlers are registered with FastAPI:

### 1. Custom Exception Handler

Handles all `MaerchenweberError` subclasses:

```python
@app.exception_handler(MaerchenweberError)
async def maerchenweber_error_handler(request: Request, exc: MaerchenweberError):
    # Logs with structured context
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

    # Returns structured JSON response
    return JSONResponse(
        status_code=determine_status_code(exc.error_code),
        content=exc.to_dict()
    )
```

### 2. Validation Error Handler

Handles Pydantic `RequestValidationError`:

```python
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Extracts field-level errors
    field_errors = [
        {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {"fields": field_errors},
            "user_message": "Ungültige Eingabe. Bitte überprüfe deine Angaben.",
            "path": request.url.path
        }
    )
```

### 3. Generic Exception Handler

Catches all unhandled exceptions:

```python
@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    # Logs full traceback for debugging
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

    # Returns sanitized error (no internal details exposed)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {"error_type": type(exc).__name__},
            "user_message": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.",
            "path": request.url.path
        }
    )
```

---

## Structured Logging

All errors are logged with structured context for observability:

```python
logger.error(
    f"Image generation failed for session {session_id}",
    extra={
        "session_id": session_id,
        "round": current_round,
        "error_type": error_type,
        "error_message": error_message
    },
    exc_info=True  # Includes full traceback
)
```

**Benefits:**
- Easy to search logs by session_id, round, error_type
- Structured data for log aggregation tools (ELK, Datadog, etc.)
- Full tracebacks for debugging

---

## Frontend Error Handling

**Location:** `src/routes/game/maerchenweber/play/+page.svelte`

### Error States

```typescript
let errorMessage = $state("");
let showError = $state(false);
let imageErrorMessage = $state("");
let imageRetryAfter = $state(0);
```

### Error Toast (Top-Center)

```svelte
{#if showError}
  <div class="fixed top-4 left-1/2 -translate-x-1/2 z-50
              bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg
              animate-slide-down">
    <p class="font-bold">Fehler!</p>
    <p>{errorMessage}</p>
  </div>
{/if}
```

### Image Error Card

```svelte
{#if imageErrorMessage}
  <div class="bg-red-50 border border-red-300 rounded-lg p-4 text-center">
    <p class="text-red-700 font-bold">🖼️ Bild konnte nicht geladen werden</p>
    <p class="text-sm text-red-600 mt-1">{imageErrorMessage}</p>
    {#if imageRetryAfter > 0}
      <p class="text-xs text-red-500 mt-1">
        Versuche es in {imageRetryAfter} Sekunden erneut.
      </p>
    {/if}
    <button
      onclick={() => pollForImage(sessionId, round)}
      class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
    >
      Erneut versuchen
    </button>
  </div>
{/if}
```

### Error Handling in API Calls

```typescript
try {
  const response = await fetch("/api/game/maerchenweber/turn", {...});

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.user_message || "Fehler beim Verarbeiten der Wahl");
  }

  const data = await response.json();
  // Process data...

} catch (error) {
  errorMessage = error instanceof Error
    ? error.message
    : "Ein unerwarteter Fehler ist aufgetreten";
  showError = true;

  // Auto-hide after 5 seconds
  setTimeout(() => { showError = false; }, 5000);
}
```

---

## Best Practices

### 1. Validate Early, Fail Fast

```python
# ✅ Good - Validate immediately
if not request.choice_text or len(request.choice_text.strip()) < 1:
    raise ValidationError(...)

# ❌ Bad - Validate late, waste resources
result = await expensive_operation()
if not valid_input:
    raise ValidationError(...)
```

### 2. Use Semantic Exception Types

```python
# ✅ Good - Clear intent
raise SessionNotFoundError(session_id)

# ❌ Bad - Generic exception
raise Exception("Session not found")
```

### 3. Include Context in Details

```python
# ✅ Good - Actionable details
raise ValidationError(
    message="Choice text too long",
    field="choice_text",
    value=len(request.choice_text),
    max_length=500
)

# ❌ Bad - No context
raise ValidationError("Invalid input")
```

### 4. Log Structured Data

```python
# ✅ Good - Structured logging
logger.error(
    "LLM generation failed",
    extra={
        "model": model,
        "prompt_length": len(prompt),
        "session_id": session_id
    }
)

# ❌ Bad - Free-text logging
logger.error(f"LLM failed for {session_id} with prompt length {len(prompt)}")
```

### 5. Never Leak Secrets or PII

```python
# ✅ Good - Sanitized
logger.error(f"Auth failed for user", extra={"user_id": user_id})

# ❌ Bad - Leaks sensitive data
logger.error(f"Auth failed: {api_key}, password: {password}")
```

### 6. Provide User-Friendly Messages

```python
# ✅ Good - Clear, actionable
user_message="Deine Antwort ist zu lang. Maximal 500 Zeichen erlaubt."

# ❌ Bad - Technical jargon
user_message="ValueError: string length exceeds max_length constraint"
```

### 7. Use Graceful Degradation

```python
# ✅ Good - Continue with fallback
try:
    image_url = await generate_image(...)
except ImageGenerationError:
    logger.warning("Image generation failed, continuing without image")
    image_url = None  # Story continues

# ❌ Bad - Block entire request
try:
    image_url = await generate_image(...)
except ImageGenerationError:
    raise  # User gets error, can't continue story
```

---

## Testing Error Handling

### Manual Testing Checklist

**Invalid Input:**
- [ ] Empty choice text → 422 validation error
- [ ] Choice text > 500 chars → 422 validation error
- [ ] Invalid session ID → 404 session not found

**Image Generation:**
- [ ] Image generation timeout → Graceful degradation, retry UI
- [ ] Image API failure → Error message with retry
- [ ] Polling timeout (15 attempts) → User-friendly error

**LLM Failures:**
- [ ] LLM API down → 500 with user message
- [ ] Invalid JSON response → Fallback behavior
- [ ] Safety violation → Fallback content (200 OK)

**Database:**
- [ ] MongoDB connection lost → 500 database error
- [ ] Invalid ObjectId → 422 validation error

### Example cURL Tests

```bash
# Test validation error
curl -X POST http://localhost:8000/adventure/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id": "valid_id", "choice_text": ""}'

# Test session not found
curl -X POST http://localhost:8000/adventure/turn \
  -H "Content-Type: application/json" \
  -d '{"session_id": "000000000000000000000000", "choice_text": "test"}'

# Test image polling
curl http://localhost:8000/adventure/image/valid_session_id/1
```

---

## Common Error Scenarios

### Scenario 1: User Submits Empty Choice

**Backend:**
```python
if not request.choice_text or len(request.choice_text.strip()) < 1:
    raise ValidationError(
        message="Choice text cannot be empty",
        field="choice_text",
        value=request.choice_text
    )
```

**Frontend:**
- Error toast appears: "Ungültige Eingabe. Bitte überprüfe deine Angaben."
- User can retry immediately

---

### Scenario 2: Image Generation Fails

**Backend:**
```python
# In image_generator.py
except Exception as e:
    logger.error(f"Image generation failed", extra={...}, exc_info=True)

    await collection.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": {
                "pending_image": {
                    "status": "failed",
                    "error": error_message,
                    "error_type": error_type
                }
            }
        }
    )
```

**Frontend:**
- Story continues immediately (no blocking)
- Image error card shows: "Bild konnte nicht geladen werden"
- "Erneut versuchen" button allows retry
- Polling stops after 15 attempts (30 seconds)

---

### Scenario 3: Session Not Found

**Backend:**
```python
session = await collection.find_one({"_id": ObjectId(session_id)})
if not session:
    raise SessionNotFoundError(session_id)
```

**Frontend:**
- Error toast: "Spielsitzung nicht gefunden"
- User redirected to home page or prompted to start new game

---

## Monitoring and Alerting

### Key Metrics to Track

1. **Error Rate by Type**
   - Validation errors (user input issues)
   - LLM errors (API failures)
   - Image errors (generation failures)
   - Database errors (connectivity issues)

2. **Response Times**
   - Story generation latency
   - Image generation latency
   - Database query times

3. **Success Rates**
   - Game completion rate
   - Image generation success rate
   - LLM API success rate

### Log Aggregation

Use structured logging extra fields for filtering:
```python
# Filter by session
session_id: "507f1f77bcf86cd799439011"

# Filter by error type
error_type: "ImageGenerationError"

# Filter by endpoint
path: "/adventure/turn"
```

---

## Troubleshooting

### Issue: Frontend Not Showing Error Messages

**Check:**
1. Error response includes `user_message` field
2. Frontend error handling catches response properly
3. Error toast state variables are reactive (`$state`)

**Solution:**
```typescript
if (!response.ok) {
  const errorData = await response.json();
  errorMessage = errorData.user_message || "Fehler aufgetreten";
  showError = true;
}
```

---

### Issue: Logs Missing Context

**Check:**
1. Using `logger.error()` with `extra` parameter
2. Including relevant fields (session_id, round, error_type)

**Solution:**
```python
logger.error(
    "Descriptive message",
    extra={
        "session_id": session_id,
        "round": round,
        "field": "value"
    },
    exc_info=True  # Include traceback
)
```

---

### Issue: Exceptions Not Being Caught

**Check:**
1. Error handlers registered in `main.py`
2. Exception inherits from correct base class
3. FastAPI middleware order

**Solution:**
```python
# In main.py
from app.error_handlers import add_error_handlers
add_error_handlers(app)
```

---

## References

- **FastAPI Error Handling:** https://fastapi.tiangolo.com/tutorial/handling-errors/
- **Structured Logging:** https://docs.python.org/3/library/logging.html
- **HTTP Status Codes:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

---

**Next Steps:**
1. Monitor error logs in production
2. Add error rate alerts (>5% error rate triggers notification)
3. Create error dashboard (Grafana/Kibana)
4. Implement automatic retry with exponential backoff for transient failures
