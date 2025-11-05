"""API router for Märchenweber adventure endpoints."""

import logging
import re
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models import (
    AdventureStartRequest,
    AdventureStartResponse,
    TurnRequest,
    AdventureStepResponse,
    DetailedErrorResponse,
)
from app.services.game_engine import get_game_engine
from app.exceptions import (
    MaerchenweberError,
    SessionNotFoundError,
    ValidationError,
    ImageGenerationError
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start")
async def start_adventure(request: AdventureStartRequest):
    """Start a new adventure (async pattern to avoid Vercel timeout).

    Creates a session immediately and generates story in background.
    Client should poll /adventure/status/{session_id} for completion.

    Args:
        request: Adventure start request with character and theme details

    Returns:
        JSON with session_id and status="generating"

    Raises:
        HTTPException: If session creation fails
    """
    try:
        logger.info(f"Received request: user_id={request.user_id}, character_name={request.character_name}")

        # Create session immediately with "generating" status
        engine = get_game_engine()
        session_id = await engine.create_session(
            user_id=request.user_id,
            character_name=request.character_name,
            character_description=request.character_description,
            story_theme=request.story_theme,
        )

        logger.info(f"Created session {session_id}, starting background generation")

        # Start background task to generate story
        import asyncio
        asyncio.create_task(engine.generate_first_story(session_id))

        return JSONResponse({
            "session_id": session_id,
            "status": "generating",
            "message": "Story is being generated. Poll /adventure/status/{session_id} for updates."
        })

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error starting adventure: {error_msg}")

        # Extract step name from error message if present (format: "Failed at step 'X': Y")
        step_match = re.search(r"Failed at step '([^']+)':", error_msg)
        step_name = step_match.group(1) if step_match else None

        error_response = DetailedErrorResponse(
            error=error_msg,
            step=step_name,
            details={"error_type": "ValidationError", "user_id": request.user_id}
        )

        return JSONResponse(
            status_code=422,
            content=error_response.model_dump()
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error starting adventure: {error_msg}")

        error_response = DetailedErrorResponse(
            error=error_msg if error_msg else "Failed to start adventure. Please try again.",
            step="Unknown",
            details={"error_type": type(e).__name__, "user_id": request.user_id}
        )

        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/turn")
async def process_turn(request: TurnRequest):
    """Process a turn in an existing adventure (async pattern).

    Takes the user's choice and starts background generation.

    Args:
        request: Turn request with session_id and choice_text

    Returns:
        JSON with session_id and status "generating"

    Raises:
        MaerchenweberError: If turn processing fails
    """
    logger.info(
        f"Processing turn",
        extra={
            "session_id": request.session_id,
            "choice_length": len(request.choice_text)
        }
    )

    # Validate input
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

    try:
        from bson import ObjectId
        from app.database import get_database

        # Mark session as generating
        db = get_database()
        collection = db["gamesessions"]

        result = await collection.update_one(
            {"_id": ObjectId(request.session_id)},
            {
                "$set": {
                    "generation_status": "generating",
                    "lastUpdated": datetime.utcnow()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Marked session {request.session_id} as generating, starting background task")

        # Start background generation
        import asyncio
        engine = get_game_engine()
        asyncio.create_task(engine.process_turn_async(request.session_id, request.choice_text))

        return JSONResponse({
            "session_id": request.session_id,
            "status": "generating",
            "message": "Story is being generated. Poll /adventure/status/{session_id} for updates."
        })

    except Exception as e:
        logger.error(f"Error starting turn generation: {e}")
        raise


@router.get("/status/{session_id}")
async def get_story_status(session_id: str):
    """Poll for story generation status (for async pattern).

    Args:
        session_id: The game session ID

    Returns:
        JSON with:
        - status: "generating" | "ready" | "error"
        - step: Story data (when ready)
        - error: Error message (if failed)

    Raises:
        HTTPException: If session not found
    """
    try:
        from bson import ObjectId
        from app.database import get_database

        db = get_database()
        collection = db["gamesessions"]

        session = await collection.find_one({"_id": ObjectId(session_id)})

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check generation status
        generation_status = session.get("generation_status", "unknown")

        if generation_status == "ready":
            # Story is complete, return it
            from app.models import AdventureStepResponse

            round_number = session.get("round", 1)

            # For round 1, include the first image. For other rounds, return None
            # (frontend will poll /adventure/image/{sessionId}/{round} separately)
            image_url = session.get("first_image_url", "") if round_number == 1 else None

            step = AdventureStepResponse(
                story_text=session.get("current_story", ""),
                image_url=image_url,
                choices=session.get("current_choices", []),
                fun_nugget=session.get("fun_nugget", ""),
                choices_history=[],
                round_number=round_number
            )

            return {
                "status": "ready",
                "session_id": session_id,
                "step": step.model_dump()
            }

        elif generation_status == "error":
            return {
                "status": "error",
                "session_id": session_id,
                "error": session.get("generation_error", "Unknown error occurred")
            }

        else:  # generating or unknown
            return {
                "status": "generating",
                "session_id": session_id,
                "message": "Story is still being generated..."
            }

    except Exception as e:
        logger.error(f"Error fetching session status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch status")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get the current state of an adventure session.

    Args:
        session_id: The game session ID

    Returns:
        Session data including history and metadata

    Raises:
        HTTPException: If session not found
    """
    try:
        from bson import ObjectId
        from app.database import get_database

        db = get_database()
        collection = db["gamesessions"]

        session = await collection.find_one({"_id": ObjectId(session_id)})

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert ObjectId to string for JSON serialization
        session["_id"] = str(session["_id"])

        return session

    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch session")


@router.get("/image/{session_id}/{round}")
async def get_image_status(session_id: str, round: int):
    """Poll for async image generation status for a specific round.

    Args:
        session_id: The game session ID
        round: The round number to check

    Returns:
        JSON with:
        - status: "generating" | "ready" | "failed" | "not_found"
        - round: Round number
        - image_url: Image URL (when ready)
        - error: Error message (if failed)
        - error_type: Type of error (if failed)
        - retry_after: Suggested retry delay in seconds

    Raises:
        SessionNotFoundError: If session not found
    """
    from bson import ObjectId
    from app.database import get_database

    logger.info(
        f"Polling for image",
        extra={"session_id": session_id, "round": round}
    )

    db = get_database()
    collection = db["gamesessions"]

    try:
        session = await collection.find_one({"_id": ObjectId(session_id)})
    except Exception as e:
        logger.error(f"Invalid session ID format: {session_id}")
        raise ValidationError(
            message="Invalid session ID format",
            field="session_id",
            value=session_id
        )

    if not session:
        raise SessionNotFoundError(session_id)

    # Check pending_image first (current async generation)
    pending_image = session.get("pending_image")

    if pending_image and pending_image.get("round") == round:
        # This round has an active/pending image
        status = pending_image.get("status", "generating")

        response = {
            "status": status,
            "round": pending_image.get("round"),
            "image_url": pending_image.get("image_url"),
            "error": pending_image.get("error"),
            "error_type": pending_image.get("error_type")
        }

        # Add retry suggestion for failed images
        if status == "failed":
            response["retry_after"] = 5
            response["user_message"] = "Das Bild konnte nicht erstellt werden. Versuche es erneut!"

        return response

    # Check image_history for completed images
    image_history = session.get("image_history", [])
    for entry in image_history:
        if entry.get("round") == round:
            # Found completed image for this round
            return {
                "status": "ready",
                "round": round,
                "image_url": entry.get("url"),
                "error": None,
                "error_type": None
            }

    # No image found for this round
    return {
        "status": "not_found",
        "round": round,
        "image_url": None,
        "error": f"No image generation found for round {round}",
        "error_type": "NOT_FOUND",
        "user_message": "Kein Bild für diese Runde gefunden."
    }


@router.get("/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get all Märchenweber sessions for a specific user.

    Returns a list of sessions with key metadata for displaying in a story list.

    Args:
        user_id: The user ID

    Returns:
        List of session summaries with:
        - session_id
        - character_name
        - story_theme
        - round (number of turns)
        - lastUpdated (timestamp)
        - first_image_url (for thumbnails)

    Raises:
        HTTPException: If query fails
    """
    try:
        from bson import ObjectId
        from app.database import get_database

        db = get_database()
        collection = db["gamesessions"]

        # Find all märchenweber sessions for this user
        # Limit results first, then sort (more efficient for large datasets)
        cursor = collection.find(
            {"userId": user_id, "gameType": "maerchenweber"},
            projection={
                "_id": 1,
                "character_name": 1,
                "story_theme": 1,
                "round": 1,
                "lastUpdated": 1,
                "image_history": 1,  # Get first image from history
                "createdAt": 1
            }
        ).sort("lastUpdated", -1).limit(50)  # Most recent 50 sessions

        sessions = await cursor.to_list(length=None)  # Get all from cursor (already limited)

        # Format for frontend
        session_list = []
        for session in sessions:
            # Get first image from image_history
            image_history = session.get("image_history", [])
            first_image_url = image_history[0]["url"] if image_history else ""

            session_list.append({
                "session_id": str(session["_id"]),
                "character_name": session.get("character_name", "Unbekannt"),
                "story_theme": session.get("story_theme", ""),
                "round": session.get("round", 1),
                "lastUpdated": session.get("lastUpdated").isoformat() if session.get("lastUpdated") else None,
                "first_image_url": first_image_url,
                "createdAt": session.get("createdAt").isoformat() if session.get("createdAt") else None,
            })

        logger.info(f"Found {len(session_list)} sessions for user {user_id}")
        return {"sessions": session_list}

    except Exception as e:
        logger.error(f"Error fetching user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user sessions")
