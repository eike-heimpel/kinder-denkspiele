"""Core game engine for Märchenweber - orchestrates the entire turn logic."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from bson import ObjectId

from app.database import get_database
from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service
from app.services.character_manager import get_character_manager
from app.services.image_generator import get_image_generator
from app.models import AdventureStepResponse
from app.utils import StepTimer

logger = logging.getLogger(__name__)


class GameEngine:
    """Core game engine implementing the Märchenweber turn logic."""

    def __init__(self):
        """Initialize the game engine."""
        self.config = get_config_loader()
        self.llm = get_llm_service()
        self.char_manager = get_character_manager()
        self.image_gen = get_image_generator()
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
            with timer.step("Generate Style Guide"):
                style_guide = await self._generate_style_guide(
                    character_name=character_name,
                    character_description=character_description,
                    story_theme=story_theme
                )
                logger.info(f"Generated style guide: {style_guide[:100]}...")

            with timer.step("Generate Opening Story + Fun Nugget (Parallel)"):
                narrator_prompt = self.config.get_prompt(
                    "character_creation",
                    character_name=character_name,
                    character_description=character_description,
                    story_theme=story_theme,
                )

                narrator_model = self.config.get_model("narrator")
                narrator_params = self.config.get_sampling_params("narrator")

                # Generate narrator story and fun nugget in parallel
                theme_context = f"Thema: {story_theme}"

                response_text, fun_nugget = await asyncio.gather(
                    self.llm.generate_text(
                        prompt=narrator_prompt,
                        model=narrator_model,
                        sampling_params=narrator_params,
                        json_mode=True,
                    ),
                    self._generate_fun_nugget(theme_context),
                )

                logger.info(f"Received response (first 200 chars): {response_text[:200]}")
                logger.info(f"Generated fun nugget: {fun_nugget[:80]}...")

            with timer.step("Parse Narrator JSON Response"):
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Response text: {response_text[:500]}")
                    raise ValueError(f"Failed to parse JSON response from narrator: {e}")

                story_text = response_data.get("story_text", "")

                # Extract 3 choices from narrator response
                main_choices = [
                    response_data.get("choice_1", "").strip(),
                    response_data.get("choice_2", "").strip(),
                    response_data.get("choice_3", "").strip(),
                ]

                logger.info(f"Extracted 3 choices: {[c[:30] + '...' for c in main_choices]}")

            with timer.step("Extract Characters from Response"):
                # Extract characters from narrator response
                characters = self.char_manager.extract_characters_from_response(
                    response_data=response_data,
                    current_round=1
                )
                logger.info(f"Extracted {len(characters)} characters from narrator")

            with timer.step("Validate Safety"):
                is_safe = await self._validate_safety(story_text)
                if not is_safe:
                    warnings.append("Unsafe content detected - using fallback story")
                    story_text = "Oh, lass uns eine andere Geschichte beginnen! Was passiert als Nächstes?"

            # Use the 3 main choices directly
            choices = main_choices

            with timer.step("Create Session Document"):
                session_doc = {
                    "userId": user_id,
                    "gameType": "maerchenweber",
                    "character_name": character_name,
                    "character_description": character_description,
                    "story_theme": story_theme,
                    "reading_level": "second_grade",
                    "history": [story_text],
                    "history_summary": "",
                    "score": 0,
                    "round": 1,
                    "createdAt": datetime.utcnow(),
                    "lastUpdated": datetime.utcnow(),
                    # v2.0 fields
                    "style_guide": style_guide,
                    "character_registry": characters,
                    "pending_image": None,
                    "image_history": []
                }

                result = await self.collection.insert_one(session_doc)
                session_id = str(result.inserted_id)
                logger.info(f"Created new adventure session: {session_id}")

            # Round 1: Wait for image (per user preference)
            with timer.step("Generate Round 1 Image (Blocking)"):
                # Get character descriptions for image generation
                char_names = [c["name"] for c in characters]

                # Log initial character registry
                logger.info(f"📊 Initial Character Registry (Round 1):")
                logger.info(f"  - Total characters: {len(characters)}")
                for char in characters:
                    has_desc = "description" in char and bool(char.get("description"))
                    desc_preview = char.get("description", "")[:60] if has_desc else "N/A"
                    logger.info(
                        f"  - {char['name']}: "
                        f"{'✅ ' + desc_preview if has_desc else '❌ NO DESCRIPTION'}"
                    )

                char_descriptions = self.char_manager.get_character_descriptions(
                    character_registry=characters,
                    character_names=char_names
                )

                # Log retrieved descriptions
                logger.info(f"📝 Retrieved descriptions for Round 1 image:")
                for name, desc in char_descriptions.items():
                    if desc:
                        logger.info(f"  ✅ {name}: {desc[:60]}...")
                    else:
                        logger.error(f"  ❌ {name}: EMPTY DESCRIPTION!")

                # Generate image using choice-based system (but with empty choice for round 1)
                # We'll use story_text as the "choice" for round 1
                choice_prompt_text = await self.image_gen._generate_choice_prompt(
                    choice_made=f"Beginne das Abenteuer als {character_name}",
                    story_text=story_text,
                    characters_in_scene=char_names,
                    character_descriptions=char_descriptions
                )

                intensity = await self.image_gen._analyze_scene_intensity(story_text)
                variance = self.image_gen.get_random_variance(intensity)

                final_prompt = self.image_gen._build_final_prompt(
                    choice_prompt=choice_prompt_text,
                    style_guide=style_guide,
                    character_descriptions=char_descriptions,
                    variance=variance
                )

                image_model = self.config.get_model("image_generator")
                image_url = await self.llm.generate_image(
                    prompt=final_prompt,
                    model=image_model,
                    aspect_ratio="4:3"
                )

                # Save image to history
                await self.collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {
                        "$push": {
                            "image_history": {
                                "round": 1,
                                "choice_made": f"Beginne das Abenteuer als {character_name}",
                                "url": image_url,
                                "prompt_used": final_prompt,
                                "characters_in_scene": char_names
                            }
                        }
                    }
                )

                logger.info(f"Generated Round 1 image: {image_url[:80]}...")

            timing_summary = timer.get_summary()
            logger.info(f"Adventure started in {timing_summary['total_ms']}ms")

            return {
                "session_id": session_id,
                "step": AdventureStepResponse(
                    story_text=story_text,
                    image_url=image_url,
                    choices=choices,
                    fun_nugget=fun_nugget,
                    choices_history=[],
                    round_number=1,
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

        Args:
            session_id: Game session ID
            choice_text: The user's choice text

        Returns:
            AdventureStepResponse with story, image=null, and choices
        """
        try:
            # 1. Load State
            session = await self.collection.find_one({"_id": ObjectId(session_id)})
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # 2. Update History
            history = session.get("history", [])
            history.append(f"[Wahl]: {choice_text}")

            # Check if we should summarize
            new_round = session.get("round", 0) + 1
            summarization_interval = self.config.get_game_mechanic("summarization_interval", 5)
            recent_turns_to_keep = self.config.get_game_mechanic("recent_turns_to_keep", 5)
            current_summary = session.get("history_summary", "")

            should_summarize = (new_round % summarization_interval) == 0 and len(history) > recent_turns_to_keep

            if should_summarize:
                logger.info(f"Round {new_round}: Generating summary")
                recent_items_count = recent_turns_to_keep * 2
                old_history = history[:-recent_items_count] if len(history) > recent_items_count else []
                recent_history = history[-recent_items_count:] if len(history) > recent_items_count else history

                if old_history:
                    new_summary = await self._summarize_history(old_history)
                    current_summary = f"{current_summary}\n\n{new_summary}" if current_summary else new_summary
                else:
                    recent_history = history

                history_text = f"{current_summary}\n\n---\n\n" + "\n\n".join(recent_history) if current_summary else "\n\n".join(recent_history)
            else:
                history_text = "\n\n".join(history)
                if current_summary:
                    history_text = f"{current_summary}\n\n---\n\n{history_text}"

            # 3. Load character registry and format for prompt
            character_registry = session.get("character_registry", [])

            wildcard = self.config.get_random_wildcard()

            narrator_prompt = self.config.get_prompt(
                "narrator",
                history=history_text,
                wildcard=wildcard,
                character_registry=character_registry  # Pass to Jinja2 template
            )

            narrator_model = self.config.get_model("narrator")
            narrator_params = self.config.get_sampling_params("narrator")

            # Generate narrator story and fun nugget in parallel
            response_text, fun_nugget = await asyncio.gather(
                self.llm.generate_text(
                    prompt=narrator_prompt,
                    model=narrator_model,
                    sampling_params=narrator_params,
                    json_mode=True,
                ),
                self._generate_fun_nugget(history_text),
            )

            # 4. Parse response
            response_data = json.loads(response_text)
            story_text = response_data.get("story_text", "")

            main_choices = [
                response_data.get("choice_1", "").strip(),
                response_data.get("choice_2", "").strip(),
                response_data.get("choice_3", "").strip(),
            ]

            logger.info(f"Extracted 3 choices: {[c[:30] + '...' for c in main_choices]}")

            # 5. Extract and merge characters
            new_characters = self.char_manager.extract_characters_from_response(
                response_data=response_data,
                current_round=new_round
            )

            updated_registry = self.char_manager.merge_characters(
                existing_registry=character_registry,
                new_characters=new_characters,
                current_round=new_round
            )

            # 6. Validate Safety
            is_safe = await self._validate_safety(story_text)
            if not is_safe:
                logger.warning(f"Unsafe content detected in session {session_id}")
                story_text = "Oh, das war eine interessante Wendung! Aber lass uns eine andere Richtung einschlagen."

            # Use the 3 main choices directly
            choices = main_choices

            # 8. Save State (WITHOUT image)
            history.append(story_text)

            update_doc = {
                "$set": {
                    "history": history,
                    "character_registry": updated_registry,
                    "round": new_round,
                    "lastUpdated": datetime.utcnow(),
                }
            }

            if should_summarize and current_summary:
                update_doc["$set"]["history_summary"] = current_summary

            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                update_doc,
            )

            # 9. Launch async image generation (fire and forget)
            style_guide = session.get("style_guide", "")
            char_names = [c["name"] for c in new_characters if "name" in c]

            # Log character registry state before retrieval
            logger.info(f"📊 Character Registry Status (Round {new_round}):")
            logger.info(f"  - Total characters in registry: {len(updated_registry)}")
            logger.info(f"  - Characters in current scene: {char_names}")
            for char in updated_registry:
                has_desc = "description" in char and bool(char.get("description"))
                logger.info(
                    f"  - {char['name']}: "
                    f"{'✅ Has description' if has_desc else '❌ NO DESCRIPTION'}"
                )

            char_descriptions = self.char_manager.get_character_descriptions(
                character_registry=updated_registry,
                character_names=char_names
            )

            # Log what descriptions were actually retrieved
            logger.info(f"📝 Retrieved descriptions for image generation:")
            for name, desc in char_descriptions.items():
                if desc:
                    logger.info(f"  ✅ {name}: {desc[:60]}...")
                else:
                    logger.error(f"  ❌ {name}: EMPTY DESCRIPTION!")

            asyncio.create_task(
                self.image_gen.generate_choice_based_image(
                    session_id=session_id,
                    choice_made=choice_text,
                    story_text=story_text,
                    style_guide=style_guide,
                    characters_in_scene=char_names,
                    character_descriptions=char_descriptions,
                    current_round=new_round
                )
            )

            logger.info(f"🚀 Launched async image generation for round {new_round}")

            # 10. Return response WITHOUT image (null)
            choices_history = self._extract_choices_from_history(history)

            return AdventureStepResponse(
                story_text=story_text,
                image_url=None,  # Image will be polled for
                choices=choices,
                fun_nugget=fun_nugget,
                choices_history=choices_history,
                round_number=new_round,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid response from narrator")
        except Exception as e:
            logger.error(f"Error processing turn: {e}")
            raise

    async def _generate_style_guide(
        self,
        character_name: str,
        character_description: str,
        story_theme: str
    ) -> str:
        """Generate a visual style guide for consistent art style.

        Args:
            character_name: Character name
            character_description: Character description
            story_theme: Story theme

        Returns:
            Style guide (1-2 sentences in English)
        """
        try:
            prompt = self.config.get_prompt(
                "style_guide_generator",
                character_name=character_name,
                character_description=character_description,
                story_theme=story_theme
            )

            model = self.config.get_model("style_guide_generator")
            params = self.config.get_sampling_params("style_guide_generator")

            result = await self.llm.generate_text(
                prompt=prompt,
                model=model,
                sampling_params=params
            )

            return result.strip()

        except Exception as e:
            logger.error(f"Error generating style guide: {e}")
            return "Watercolor fairy tale style with soft pastel colors, dreamy magical atmosphere"

    async def _validate_safety(self, german_text: str) -> bool:
        """Validate that the text is appropriate for a 7-year-old."""
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

            return "SAFE" in response.upper()

        except Exception as e:
            logger.error(f"Safety validation error: {e}")
            return True


    async def _summarize_history(self, history: List[str]) -> str:
        """Summarize story history to keep context manageable."""
        try:
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

            logger.info(f"Generated summary ({len(summary)} chars)")
            return summary.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Die Geschichte bisher: Du hast ein spannendes Abenteuer erlebt."

    async def _generate_fun_nugget(self, current_story: str) -> str:
        """Generate a fun fact or teaser related to the current story."""
        try:
            fun_nugget_prompt = self.config.get_prompt(
                "fun_nugget",
                current_story=current_story,
            )

            fun_nugget_model = self.config.get_model("fun_nugget_generator")
            fun_nugget_params = self.config.get_sampling_params("fun_nugget_generator")

            fun_nugget = await self.llm.generate_text(
                prompt=fun_nugget_prompt,
                model=fun_nugget_model,
                sampling_params=fun_nugget_params,
            )

            logger.info(f"Generated fun nugget: {fun_nugget[:80]}...")
            return fun_nugget.strip().strip('"').strip("'")

        except Exception as e:
            logger.error(f"Error generating fun nugget: {e}")
            return "Wusstest du? Jede Geschichte, die du erlebst, ist einzigartig und magisch!"

    def _extract_choices_from_history(self, history: List[str]) -> List[str]:
        """Extract user choices from history for journey recap."""
        choices = []
        for entry in history:
            if entry.startswith("[Wahl]: "):
                choice_text = entry[len("[Wahl]: "):]
                choices.append(choice_text)
        return choices

    async def create_session(
        self,
        user_id: str,
        character_name: str,
        character_description: str,
        story_theme: str,
    ) -> str:
        """Create a new session immediately with 'generating' status.

        Args:
            user_id: User ID from the main app
            character_name: Name of the character
            character_description: Description of the character
            story_theme: Theme/setting of the story

        Returns:
            session_id: The created session ID
        """
        logger.info(f"Creating session for user {user_id}")

        session_doc = {
            "userId": user_id,
            "gameType": "maerchenweber",
            "character_name": character_name,
            "character_description": character_description,
            "story_theme": story_theme,
            "reading_level": "second_grade",
            "generation_status": "generating",  # Status for polling
            "history": [],
            "history_summary": "",
            "score": 0,
            "round": 1,
            "createdAt": datetime.utcnow(),
            "lastUpdated": datetime.utcnow(),
            "style_guide": "",
            "character_registry": [],
            "pending_image": None,
            "image_history": [],
            "current_story": "",
            "current_choices": [],
            "fun_nugget": ""
        }

        result = await self.collection.insert_one(session_doc)
        session_id = str(result.inserted_id)
        logger.info(f"Created session {session_id} with status 'generating'")
        return session_id

    async def generate_first_story(self, session_id: str):
        """Background task to generate the first story for a session.

        Args:
            session_id: The session ID to generate story for
        """
        try:
            logger.info(f"Starting background story generation for session {session_id}")

            # Get session to retrieve character details
            session = await self.collection.find_one({"_id": ObjectId(session_id)})
            if not session:
                logger.error(f"Session {session_id} not found")
                return

            # Run the full story generation logic
            result = await self.start_adventure(
                user_id=session["userId"],
                character_name=session["character_name"],
                character_description=session["character_description"],
                story_theme=session["story_theme"],
            )

            # Update session with the generated story
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "generation_status": "ready",
                        "current_story": result["step"].story_text,
                        "current_choices": result["step"].choices,
                        "first_image_url": result["step"].image_url,
                        "fun_nugget": result["step"].fun_nugget,
                        "history": [result["step"].story_text],
                        "style_guide": session.get("style_guide", ""),
                        "character_registry": session.get("character_registry", []),
                        "image_history": session.get("image_history", []),
                        "lastUpdated": datetime.utcnow()
                    }
                }
            )

            logger.info(f"Successfully generated story for session {session_id}")

        except Exception as e:
            logger.error(f"Error generating story for session {session_id}: {e}")

            # Mark session as error
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "generation_status": "error",
                        "generation_error": str(e),
                        "lastUpdated": datetime.utcnow()
                    }
                }
            )


    async def process_turn_async(self, session_id: str, choice_text: str):
        """Background task to process a turn asynchronously.

        Args:
            session_id: The game session ID
            choice_text: The user's choice text
        """
        try:
            logger.info(f"Starting background turn processing for session {session_id}")

            # Run the full turn generation logic
            result = await self.process_turn(
                session_id=session_id,
                choice_text=choice_text,
            )

            # Update session with the generated story
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "generation_status": "ready",
                        "current_story": result.story_text,
                        "current_choices": result.choices,
                        "fun_nugget": result.fun_nugget,
                        "lastUpdated": datetime.utcnow()
                    }
                }
            )

            logger.info(f"Successfully generated turn for session {session_id}")

        except Exception as e:
            logger.error(f"Error generating turn for session {session_id}: {e}")

            # Mark session as error
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "generation_status": "error",
                        "generation_error": str(e),
                        "lastUpdated": datetime.utcnow()
                    }
                }
            )


def get_game_engine() -> GameEngine:
    """Get an instance of the game engine."""
    return GameEngine()
