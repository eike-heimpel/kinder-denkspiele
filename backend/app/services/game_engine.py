"""Core game engine for Märchenweber - orchestrates the entire turn logic."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from bson import ObjectId

from app.database import get_database
from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service
from app.models import AdventureStepResponse
from app.utils import StepTimer

logger = logging.getLogger(__name__)


class GameEngine:
    """Core game engine implementing the Märchenweber turn logic."""

    def __init__(self):
        """Initialize the game engine."""
        self.config = get_config_loader()
        self.llm = get_llm_service()
        self.db = get_database()
        self.collection = self.db["gamesessions"]

    async def start_adventure(
        self,
        user_id: str,
        character_name: str,
        character_description: str,
        story_theme: str,
    ) -> Dict[str, Any]:
        """Start a new adventure.

        Args:
            user_id: User ID from the main app
            character_name: Name of the character
            character_description: Description of the character
            story_theme: Theme/setting of the story

        Returns:
            Dictionary with session_id and first step
        """
        timer = StepTimer()
        warnings = []

        try:
            with timer.step("Create Session Document"):
                session_doc = {
                    "userId": user_id,
                    "gameType": "maerchenweber",
                    "character_name": character_name,
                    "character_description": character_description,
                    "story_theme": story_theme,
                    "reading_level": "second_grade",
                    "history": [],
                    "score": 0,
                    "round": 1,
                    "createdAt": datetime.utcnow(),
                    "lastUpdated": datetime.utcnow(),
                }

                result = await self.collection.insert_one(session_doc)
                session_id = str(result.inserted_id)
                logger.info(f"Created new adventure session: {session_id}")

            with timer.step("Generate Opening Story (Narrator LLM)"):
                prompt = self.config.get_prompt(
                    "character_creation",
                    character_name=character_name,
                    character_description=character_description,
                    story_theme=story_theme,
                )

                model = self.config.get_model("narrator")
                sampling_params = self.config.get_sampling_params("narrator")

                response_text = await self.llm.generate_text(
                    prompt=prompt,
                    model=model,
                    sampling_params=sampling_params,
                    json_mode=True,
                )

                logger.info(f"Received response text (first 200 chars): {response_text[:200]}")

            with timer.step("Parse Narrator JSON Response"):
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Response text: {response_text[:500]}")
                    raise ValueError(f"Failed to parse JSON response from narrator: {e}")

                story_text = response_data.get("story_text", "")
                image_prompt = response_data.get("image_prompt", "")

            with timer.step("Validate Safety (Validator LLM)"):
                is_safe = await self._validate_safety(story_text)
                if not is_safe:
                    warnings.append("Unsafe content detected - using fallback story")
                    story_text = "Oh, lass uns eine andere Geschichte beginnen! Was passiert als Nächstes?"
                    image_prompt = "Ein magisches Märchenbuch mit bunten Farben"

            with timer.step("Generate 3 Choices (Council of Choices)"):
                choices = await self._generate_choices(story_text)

            with timer.step("Generate Image (Image LLM)"):
                image_url = await self._generate_image(image_prompt)

            with timer.step("Save to Database"):
                await self.collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {
                        "$push": {"history": story_text},
                        "$set": {"lastUpdated": datetime.utcnow()},
                    },
                )

            timing_summary = timer.get_summary()
            logger.info(f"Adventure started successfully in {timing_summary['total_ms']}ms")

            return {
                "session_id": session_id,
                "step": AdventureStepResponse(
                    story_text=story_text,
                    image_url=image_url,
                    choices=choices,
                    timing=timing_summary,
                    warnings=warnings,
                ),
            }

        except Exception as e:
            timing_summary = timer.get_summary()
            logger.error(f"Error starting adventure after {timing_summary.get('total_ms', 0)}ms: {e}")
            raise ValueError(f"Failed at step '{timer.current_step}': {str(e)}")

    async def process_turn(
        self,
        session_id: str,
        choice_text: str,
    ) -> AdventureStepResponse:
        """Process a single turn in the adventure.

        This implements the complete "Turn Logic" chain from the PRD:
        1. Load State
        2. Update History
        3. Prompt Narrator (with wildcard)
        4. Validate Narrative
        5. Generate Choices (Council of Choices)
        6. Generate Image
        7. Save State
        8. Return Response

        Args:
            session_id: Game session ID
            choice_text: The user's choice text

        Returns:
            AdventureStepResponse with story, image, and choices
        """
        try:
            # 1. Load State
            session = await self.collection.find_one({"_id": ObjectId(session_id)})
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # 2. Update History (append user choice)
            history = session.get("history", [])
            history.append(f"[Wahl]: {choice_text}")

            # 3. Prompt Narrator with Wildcard
            wildcard = self.config.get_random_wildcard()
            history_text = "\n\n".join(history)

            narrator_prompt = self.config.get_prompt(
                "narrator",
                history=history_text,
                wildcard=wildcard,
            )

            narrator_model = self.config.get_model("narrator")
            narrator_params = self.config.get_sampling_params("narrator")

            response_text = await self.llm.generate_text(
                prompt=narrator_prompt,
                model=narrator_model,
                sampling_params=narrator_params,
                json_mode=True,
            )

            # Parse narrator response
            response_data = json.loads(response_text)
            story_text = response_data.get("story_text", "")
            image_prompt = response_data.get("image_prompt", "")

            # 4. Validate Narrative (Safety Check)
            is_safe = await self._validate_safety(story_text)
            if not is_safe:
                logger.warning(f"Unsafe content detected in session {session_id}")
                story_text = "Oh, das war eine interessante Wendung! Aber lass uns eine andere Richtung einschlagen. Was passiert nun?"
                image_prompt = "Ein magisches Märchenbuch mit bunten Seiten"

            # 5. Generate Choices (Council of Choices - 3 parallel calls)
            choices = await self._generate_choices(history_text + "\n\n" + story_text)

            # 6. Generate Image
            image_url = await self._generate_image(image_prompt)

            # 7. Save State
            history.append(story_text)
            new_round = session.get("round", 0) + 1

            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "history": history,
                        "round": new_round,
                        "lastUpdated": datetime.utcnow(),
                    }
                },
            )

            logger.info(f"Processed turn for session {session_id}, round {new_round}")

            # 8. Return Response
            return AdventureStepResponse(
                story_text=story_text,
                image_url=image_url,
                choices=choices,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid response from narrator")
        except Exception as e:
            logger.error(f"Error processing turn: {e}")
            raise

    async def _validate_safety(self, german_text: str) -> bool:
        """Validate that the text is appropriate for a 7-year-old.

        Args:
            german_text: The German text to validate

        Returns:
            True if safe, False if unsafe
        """
        try:
            validator_prompt = self.config.get_prompt(
                "validator",
                german_text=german_text,
            )

            validator_model = self.config.get_model("validator")
            validator_params = self.config.get_sampling_params("validator")

            response = await self.llm.generate_text(
                prompt=validator_prompt,
                model=validator_model,
                sampling_params=validator_params,
            )

            # Check if response contains "SAFE"
            return "SAFE" in response.upper()

        except Exception as e:
            logger.error(f"Safety validation error: {e}")
            # Default to safe if validation fails
            return True

    async def _generate_choices(self, history: str) -> List[str]:
        """Generate three choices using the Council of Choices.

        This makes 3 parallel API calls to different models with different prompts.

        Args:
            history: The full story history so far

        Returns:
            List of 3 choice strings
        """
        agent_names = ["brave", "silly", "careful"]
        agent_models = []

        try:
            # Prepare prompts for all three choice agents
            brave_prompt = self.config.get_prompt("choice_prompts.brave", history=history)
            silly_prompt = self.config.get_prompt("choice_prompts.silly", history=history)
            careful_prompt = self.config.get_prompt("choice_prompts.careful", history=history)

            # Get models
            brave_model = self.config.get_model("choice_agent_brave")
            silly_model = self.config.get_model("choice_agent_silly")
            careful_model = self.config.get_model("choice_agent_careful")
            agent_models = [brave_model, silly_model, careful_model]

            # Get sampling params
            brave_params = self.config.get_sampling_params("choice_agent_brave")
            silly_params = self.config.get_sampling_params("choice_agent_silly")
            careful_params = self.config.get_sampling_params("choice_agent_careful")

            # Generate all three choices in parallel
            choices = []

            # Generate each choice sequentially (httpx gather not available, use asyncio)
            import asyncio
            brave_task = self.llm.generate_text(brave_prompt, brave_model, brave_params)
            silly_task = self.llm.generate_text(silly_prompt, silly_model, silly_params)
            careful_task = self.llm.generate_text(careful_prompt, careful_model, careful_params)

            results = await asyncio.gather(brave_task, silly_task, careful_task, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    agent_name = agent_names[i]
                    model_name = agent_models[i] if i < len(agent_models) else "unknown"
                    logger.error(f"❌ Choice agent '{agent_name}' ({model_name}) failed: {type(result).__name__}: {str(result)}")
                    # Use fallback choice
                    fallback_choices = ["Ich gehe mutig weiter", "Ich lache fröhlich", "Ich warte vorsichtig ab"]
                    choices.append(fallback_choices[i])
                else:
                    # Clean up the response
                    choice_text = result.strip().strip('"').strip("'")
                    agent_name = agent_names[i]
                    logger.info(f"✅ Choice agent '{agent_name}': {choice_text[:50]}...")
                    choices.append(choice_text)

            return choices[:3]  # Ensure exactly 3 choices

        except Exception as e:
            logger.error(f"❌ Critical error generating choices: {type(e).__name__}: {str(e)}")
            # Return fallback choices
            return [
                "Ich gehe mutig vorwärts",
                "Ich mache etwas Lustiges",
                "Ich schaue mich vorsichtig um",
            ]

    async def _generate_image(self, german_image_prompt: str) -> str:
        """Generate an image from a German prompt.

        First translates the prompt to English, then generates the image.

        Args:
            german_image_prompt: Image description in German

        Returns:
            Image URL (data URL or hosted URL)
        """
        try:
            # Translate to English for better image generation
            translator_prompt = self.config.get_prompt(
                "image_prompt_translator",
                german_image_prompt=german_image_prompt,
            )

            translator_model = self.config.get_model("image_translator")
            translator_params = self.config.get_sampling_params("image_translator")

            english_prompt = await self.llm.generate_text(
                prompt=translator_prompt,
                model=translator_model,
                sampling_params=translator_params,
            )

            logger.info(f"Translated image prompt: {english_prompt[:100]}")

            # Generate image
            image_model = self.config.get_model("image_generator")
            image_url = await self.llm.generate_image(
                prompt=english_prompt,
                model=image_model,
                aspect_ratio="4:3",  # Good for storybook illustrations
            )

            return image_url

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            # Return placeholder SVG
            return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23fef3c7'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%2378350f' font-size='32' font-family='sans-serif'%3E📖 Märchenweber%3C/text%3E%3C/svg%3E"


def get_game_engine() -> GameEngine:
    """Get an instance of the game engine.

    Returns:
        GameEngine instance
    """
    return GameEngine()
