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
                    "history_summary": "",  # Will accumulate summaries of old turns
                    "image_history": [],  # Array of {round, url, description} objects
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
                # First image - no previous image to reference
                image_url = await self._generate_image(
                    german_image_prompt=image_prompt,
                    previous_image_url=None,
                    first_image_description=None
                )

            with timer.step("Generate Image Description for Future Consistency"):
                # Ask the translator to describe the image style for future consistency
                description_prompt = f"""Beschreibe kurz den Bildstil und die Charaktere in diesem Bild für ein Märchenbuch:

                Bildprompt: {image_prompt}

                Antworte in 1-2 Sätzen auf Deutsch (z.B. "Bunter Cartoon-Stil mit einer kleinen Prinzessin in einem lila Kleid")."""

                model = self.config.get_model("image_translator")
                sampling_params = self.config.get_sampling_params("image_translator")

                first_image_description = await self.llm.generate_text(
                    prompt=description_prompt,
                    model=model,
                    sampling_params=sampling_params,
                )

                logger.info(f"First image description: {first_image_description[:100]}")

            with timer.step("Save to Database"):
                await self.collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {
                        "$push": {
                            "history": story_text,
                            "image_history": {
                                "round": 1,
                                "url": image_url,
                                "description": first_image_description,
                            },
                        },
                        "$set": {
                            "lastUpdated": datetime.utcnow(),
                            "first_image_url": image_url,  # Keep for backwards compatibility
                            "first_image_description": first_image_description,
                            "previous_image_url": image_url,  # Current image for style consistency
                        },
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

            # Check if we should summarize history
            new_round = session.get("round", 0) + 1
            summarization_interval = self.config.get_game_mechanic("summarization_interval", 5)
            recent_turns_to_keep = self.config.get_game_mechanic("recent_turns_to_keep", 5)
            current_summary = session.get("history_summary", "")

            should_summarize = (new_round % summarization_interval) == 0 and len(history) > recent_turns_to_keep

            if should_summarize:
                logger.info(f"Round {new_round}: Generating summary (interval={summarization_interval})")

                # Split history: old (to summarize) and recent (keep raw)
                # Each turn adds 2 items: story + choice, so recent_turns * 2 items
                recent_items_count = recent_turns_to_keep * 2
                old_history = history[:-recent_items_count] if len(history) > recent_items_count else []
                recent_history = history[-recent_items_count:] if len(history) > recent_items_count else history

                # Generate summary of old history (if exists)
                if old_history:
                    new_summary = await self._summarize_history(old_history)
                    # Append to existing summary if present
                    if current_summary:
                        current_summary = f"{current_summary}\n\n{new_summary}"
                    else:
                        current_summary = new_summary
                else:
                    # Not enough history yet, keep all
                    recent_history = history

                # Build history text for narrator: summary + recent turns
                if current_summary:
                    history_text = f"{current_summary}\n\n---\n\n" + "\n\n".join(recent_history)
                else:
                    history_text = "\n\n".join(recent_history)

                logger.info(f"Using summary ({len(current_summary)} chars) + {len(recent_history)} recent items")
            else:
                # No summarization this turn, use full history
                history_text = "\n\n".join(history)
                if current_summary:
                    history_text = f"{current_summary}\n\n---\n\n{history_text}"

            # 3. Prompt Narrator with Wildcard
            wildcard = self.config.get_random_wildcard()

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

            # 6. Generate Image (conditionally based on round number)
            # Note: new_round was already calculated earlier in step 2
            image_generation_interval = self.config.get_game_mechanic("image_generation_interval", 5)

            # Generate new image every N turns (1, 6, 11, 16, etc. if interval=5)
            # Formula: round % interval == 1 (so rounds 1, 6, 11, 16...)
            should_generate_image = (new_round % image_generation_interval) == 1

            previous_image_url = session.get("previous_image_url")
            first_image_description = session.get("first_image_description")

            if should_generate_image:
                logger.info(f"Round {new_round}: Generating NEW image (interval={image_generation_interval})")
                image_url = await self._generate_image(
                    german_image_prompt=image_prompt,
                    previous_image_url=previous_image_url,
                    first_image_description=first_image_description
                )

                # Save to image history
                image_history_entry = {
                    "round": new_round,
                    "url": image_url,
                    "description": image_prompt,
                }
            else:
                logger.info(f"Round {new_round}: Reusing previous image (next image at round {new_round + (image_generation_interval - (new_round % image_generation_interval))})")
                image_url = previous_image_url  # Reuse last generated image
                image_history_entry = None  # Don't add to history

            # 7. Save State
            history.append(story_text)

            update_doc = {
                "$set": {
                    "history": history,
                    "round": new_round,
                    "lastUpdated": datetime.utcnow(),
                    "previous_image_url": image_url,  # Always update (either new or reused)
                }
            }

            # Save summary if we generated one
            if should_summarize and current_summary:
                update_doc["$set"]["history_summary"] = current_summary

            # Only push to image_history if we generated a new image
            if image_history_entry:
                update_doc["$push"] = {"image_history": image_history_entry}

            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                update_doc,
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
        """Generate 4 choices: 3 coherent choices + 1 wild card.

        Step 1: Generate 3 coherent choices together (single LLM call)
        Step 2: Generate 1 creative wild card choice with context (separate call)

        This approach maintains coherence while ensuring diversity.

        Args:
            history: The full story history so far

        Returns:
            List of 4 choice strings
        """
        # Step 1: Generate 3 main choices (unified call)
        logger.info("Generating 3 coherent choices...")

        unified_prompt = self.config.get_prompt("choice_prompts.unified_choices", history=history)
        unified_model = self.config.get_model("choice_agent_unified")
        unified_params = self.config.get_sampling_params("choice_agent_unified")

        # Define schema for choice generation
        choices_schema = {
            "name": "choices_response",
            "schema": {
                "type": "object",
                "properties": {
                    "choice_1": {"type": "string", "description": "First choice in German"},
                    "choice_2": {"type": "string", "description": "Second choice in German"},
                    "choice_3": {"type": "string", "description": "Third choice in German"}
                },
                "required": ["choice_1", "choice_2", "choice_3"],
                "additionalProperties": False
            }
        }

        unified_response = await self.llm.generate_text(
            prompt=unified_prompt,
            model=unified_model,
            sampling_params=unified_params,
            json_mode=True,
            json_schema=choices_schema,
        )

        # Parse the JSON response (no fallback - fail if it fails)
        choices_data = json.loads(unified_response)
        main_choices = [
            choices_data["choice_1"].strip(),
            choices_data["choice_2"].strip(),
            choices_data["choice_3"].strip(),
        ]

        logger.info(f"✅ Generated 3 main choices: {[c[:30] + '...' for c in main_choices]}")

        # Step 2: Generate wild card choice with context
        logger.info("Generating wild card choice...")

        wildcard_prompt = self.config.get_prompt(
            "choice_prompts.wildcard_choice",
            history=history,
            choice_1=main_choices[0],
            choice_2=main_choices[1],
            choice_3=main_choices[2],
        )

        wildcard_model = self.config.get_model("choice_agent_wildcard")
        wildcard_params = self.config.get_sampling_params("choice_agent_wildcard")

        wildcard_response = await self.llm.generate_text(
            prompt=wildcard_prompt,
            model=wildcard_model,
            sampling_params=wildcard_params,
        )

        wildcard_choice = wildcard_response.strip().strip('"').strip("'")
        logger.info(f"✅ Generated wild card choice: {wildcard_choice[:50]}...")

        # Combine all 4 choices
        all_choices = main_choices + [wildcard_choice]
        return all_choices

    async def _generate_image(
        self,
        german_image_prompt: str,
        previous_image_url: str | None = None,
        first_image_description: str | None = None
    ) -> str:
        """Generate an image from a German prompt with style consistency.

        First translates the prompt to English, then generates the image.
        If previous_image_url is provided, includes it for style consistency.
        If first_image_description is provided, adds style instructions.

        Args:
            german_image_prompt: Image description in German
            previous_image_url: Optional URL of previous image for consistency
            first_image_description: Optional description of the first image's style

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

            # Generate image with style consistency
            image_model = self.config.get_model("image_generator")
            image_url = await self.llm.generate_image(
                prompt=english_prompt,
                model=image_model,
                aspect_ratio="4:3",  # Good for storybook illustrations
                previous_image_url=previous_image_url,
                style_description=first_image_description,
            )

            return image_url

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            # Return placeholder SVG
            return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600'%3E%3Crect width='800' height='600' fill='%23fef3c7'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%2378350f' font-size='32' font-family='sans-serif'%3E📖 Märchenweber%3C/text%3E%3C/svg%3E"

    async def _summarize_history(self, history: List[str]) -> str:
        """Summarize story history to keep context manageable.

        Takes the full history and creates a concise summary of older events,
        allowing us to keep only recent turns in full detail.

        Args:
            history: List of story segments and choices to summarize

        Returns:
            Summary text in German
        """
        try:
            # Join history for summarization
            history_text = "\n\n".join(history)

            summarizer_prompt = self.config.get_prompt(
                "summarizer",
                history_to_summarize=history_text,
            )

            summarizer_model = self.config.get_model("summarizer")
            summarizer_params = self.config.get_sampling_params("summarizer")

            summary = await self.llm.generate_text(
                prompt=summarizer_prompt,
                model=summarizer_model,
                sampling_params=summarizer_params,
            )

            logger.info(f"Generated summary ({len(summary)} chars) from {len(history_text)} chars of history")
            return summary.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Return a basic fallback summary
            return "Die Geschichte bisher: Du hast ein spannendes Abenteuer erlebt."


def get_game_engine() -> GameEngine:
    """Get an instance of the game engine.

    Returns:
        GameEngine instance
    """
    return GameEngine()
