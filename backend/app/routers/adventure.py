"""API router for Märchenweber adventure endpoints."""

import logging
import re
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

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=AdventureStartResponse)
async def start_adventure(request: AdventureStartRequest):
    """Start a new adventure.

    Creates a new game session and returns the opening scene with choices.

    Args:
        request: Adventure start request with character and theme details

    Returns:
        AdventureStartResponse with session_id and first step

    Raises:
        HTTPException: If adventure creation fails
    """
    try:
        logger.info(f"Received request: user_id={request.user_id}, character_name={request.character_name}")
        logger.info(f"Starting adventure for user {request.user_id}")

        engine = get_game_engine()
        result = await engine.start_adventure(
            user_id=request.user_id,
            character_name=request.character_name,
            character_description=request.character_description,
            story_theme=request.story_theme,
        )

        return AdventureStartResponse(
            session_id=result["session_id"],
            step=result["step"],
        )

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


@router.post("/turn", response_model=AdventureStepResponse)
async def process_turn(request: TurnRequest):
    """Process a turn in an existing adventure.

    Takes the user's choice and generates the next story segment.

    Args:
        request: Turn request with session_id and choice_text

    Returns:
        AdventureStepResponse with new story, image, and choices

    Raises:
        HTTPException: If turn processing fails
    """
    try:
        logger.info(f"Processing turn for session {request.session_id}")

        engine = get_game_engine()
        result = await engine.process_turn(
            session_id=request.session_id,
            choice_text=request.choice_text,
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error processing turn: {e}")

        # Check if it's a "session not found" error
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing turn: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process turn. Please try again.",
        )


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
        cursor = collection.find(
            {"userId": user_id, "gameType": "maerchenweber"}
        ).sort("lastUpdated", -1)  # Most recent first

        sessions = await cursor.to_list(length=100)  # Limit to 100 sessions

        # Format for frontend
        session_list = []
        for session in sessions:
            session_list.append({
                "session_id": str(session["_id"]),
                "character_name": session.get("character_name", "Unbekannt"),
                "story_theme": session.get("story_theme", ""),
                "round": session.get("round", 1),
                "lastUpdated": session.get("lastUpdated").isoformat() if session.get("lastUpdated") else None,
                "first_image_url": session.get("first_image_url", ""),
                "createdAt": session.get("createdAt").isoformat() if session.get("createdAt") else None,
            })

        logger.info(f"Found {len(session_list)} sessions for user {user_id}")
        return {"sessions": session_list}

    except Exception as e:
        logger.error(f"Error fetching user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user sessions")
