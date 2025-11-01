"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AdventureStartRequest(BaseModel):
    """Request to start a new adventure."""

    character_name: str = Field(..., min_length=1, max_length=100)
    character_description: str = Field(..., min_length=1, max_length=200)
    story_theme: str = Field(..., min_length=1, max_length=200)
    user_id: str = Field(..., description="User ID from the main app")


class TurnRequest(BaseModel):
    """Request to process a turn in an adventure."""

    session_id: str = Field(..., description="Game session ID")
    choice_text: str = Field(..., min_length=1, max_length=500)


class StepTimingInfo(BaseModel):
    """Timing information for a pipeline step."""

    name: str
    duration_ms: float
    status: str  # "success" or "error"
    error: Optional[str] = None


class AdventureStepResponse(BaseModel):
    """Response containing a single step in the adventure."""

    story_text: str = Field(..., description="The new paragraph of the story in German")
    image_url: str = Field(..., description="URL to the generated image")
    choices: List[str] = Field(..., min_length=3, max_length=4, description="3-4 choices in German (3 main + 1 wild card)")
    timing: Optional[Dict[str, Any]] = Field(None, description="Timing breakdown for debugging")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")


class AdventureStartResponse(BaseModel):
    """Response when starting a new adventure."""

    session_id: str = Field(..., description="Unique session identifier")
    step: AdventureStepResponse = Field(..., description="First step of the adventure")


class DetailedErrorResponse(BaseModel):
    """Detailed error response with context."""

    error: str = Field(..., description="Error message")
    step: Optional[str] = Field(None, description="Which pipeline step failed")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    timing: Optional[Dict[str, Any]] = Field(None, description="Timing info up to failure point")


class GameSession(BaseModel):
    """MongoDB document model for game session."""

    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    game_type: str = "maerchenweber"
    character_name: str
    character_description: str
    story_theme: str
    reading_level: str = "second_grade"
    history: List[str] = Field(default_factory=list, description="Alternating story paragraphs and choices")
    score: int = 0
    round: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Image consistency tracking
    first_image_url: Optional[str] = Field(None, description="URL of the first generated image")
    first_image_description: Optional[str] = Field(None, description="Description of first image for style consistency")
    previous_image_url: Optional[str] = Field(None, description="URL of the most recent image")

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
