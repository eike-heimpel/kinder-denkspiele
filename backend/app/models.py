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
    image_url: Optional[str] = Field(None, description="URL to the generated image (null for async generation)")
    choices: List[str] = Field(..., min_length=3, max_length=3, description="3 choices in German")
    fun_nugget: Optional[str] = Field(None, description="Fun fact or teaser (1 sentence) generated during loading")
    choices_history: List[str] = Field(default_factory=list, description="List of all choices made so far (for journey recap)")
    round_number: Optional[int] = Field(None, description="Current round number")
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


class Character(BaseModel):
    """Character in the story with consistent visual description."""

    name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual appearance description")
    first_seen_round: int = Field(..., description="Round when character first appeared")
    last_seen_round: int = Field(..., description="Round when character was last seen")


class PendingImage(BaseModel):
    """Status tracking for async image generation."""

    status: str = Field(..., description="generating | ready | failed")
    round: int = Field(..., description="Round number for this image")
    image_url: Optional[str] = Field(None, description="Generated image URL (when ready)")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="When generation completed")
    error: Optional[str] = Field(None, description="Error message if failed")


class ImageHistoryEntry(BaseModel):
    """Historical record of a generated image."""

    round: int = Field(..., description="Round number")
    choice_made: str = Field(..., description="User's choice that led to this image")
    url: str = Field(..., description="Image URL")
    prompt_used: str = Field(..., description="Prompt used for generation")
    characters_in_scene: List[str] = Field(default_factory=list, description="Character names present")


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

    # New v2.0 fields
    style_guide: Optional[str] = Field(None, description="Visual style guide for consistent art style")
    character_registry: List[Character] = Field(default_factory=list, description="Persistent character descriptions")
    pending_image: Optional[PendingImage] = Field(None, description="Current async image generation status")
    image_history: List[ImageHistoryEntry] = Field(default_factory=list, description="All generated images")

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
