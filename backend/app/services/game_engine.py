"""Core game engine for Märchenweber - orchestrates the entire turn logic."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId

from app.database import get_database
from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service
from app.services.character_manager import get_character_manager
from app.services.image_generator import get_image_generator
from app.services.story_generator import get_story_generator
from app.services.session_manager import get_session_manager
from app.services.history_builder import get_history_builder
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
        self.story_gen = get_story_generator()
        self.session_mgr = get_session_manager()
        self.history_builder = get_history_builder()
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
                style_guide = await self.story_gen.generate_style_guide(
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

                theme_context = f"Thema: {story_theme}"

                response_text, fun_nugget = await asyncio.gather(
                    self.llm.generate_text(
                        prompt=narrator_prompt,
                        model=narrator_model,
                        sampling_params=narrator_params,
                        json_mode=True,
                    ),
                    self.story_gen.generate_fun_nugget(theme_context),
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

                main_choices = [
                    response_data.get("choice_1", "").strip(),
                    response_data.get("choice_2", "").strip(),
                    response_data.get("choice_3", "").strip(),
                ]

                logger.info(f"Extracted 3 choices: {[c[:30] + '...' for c in main_choices]}")

            with timer.step("Extract Characters from Response"):
                characters = self.char_manager.extract_characters_from_response(
                    response_data=response_data,
                    current_round=1
                )
                logger.info(f"Extracted {len(characters)} characters from narrator")

            with timer.step("Validate Safety"):
                is_safe = await self.story_gen.validate_safety(story_text)
                if not is_safe:
                    warnings.append("Unsafe content detected - using fallback story")
                    story_text = "Oh, lass uns eine andere Geschichte beginnen! Was passiert als Nächstes?"

            choices = main_choices

            with timer.step("Create Session Document"):
                first_turn = {
                    "round": 1,
                    "choice_made": None,
                    "story_text": story_text,
                    "choices": choices,
                    "image_url": None,
                    "fun_nugget": fun_nugget,
                    "started_at": datetime.utcnow(),
                    "completed_at": None
                }

                session_doc = {
                    "userId": user_id,
                    "gameType": "maerchenweber",
                    "character_name": character_name,
                    "character_description": character_description,
                    "story_theme": story_theme,
                    "reading_level": "second_grade",
                    "turns": [first_turn],
                    "summary": "",
                    "score": 0,
                    "round": 1,
                    "createdAt": datetime.utcnow(),
                    "lastUpdated": datetime.utcnow(),
                    "generation_status": "ready",
                    "style_guide": style_guide,
                    "character_registry": characters,
                    "pending_image": None
                }

                result = await self.collection.insert_one(session_doc)
                session_id = str(result.inserted_id)
                logger.info(f"Created new adventure session: {session_id}")

            with timer.step("Generate Round 1 Image (Blocking)"):
                char_names = [c["name"] for c in characters]

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

                logger.info(f"📝 Retrieved descriptions for Round 1 image:")
                for name, desc in char_descriptions.items():
                    if desc:
                        logger.info(f"  ✅ {name}: {desc[:60]}...")
                    else:
                        logger.error(f"  ❌ {name}: EMPTY DESCRIPTION!")

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

                await self.collection.update_one(
                    {"_id": ObjectId(session_id), "turns.round": 1},
                    {
                        "$set": {
                            "turns.$.image_url": image_url,
                            "turns.$.completed_at": datetime.utcnow()
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
            await self.session_mgr.recover_incomplete_turns(session_id)

            session = await self.session_mgr.load_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            turns = session.get("turns", [])
            new_round = session.get("round", 0) + 1

            summarization_interval = self.config.get_game_mechanic("summarization_interval", 5)
            recent_turns_to_keep = self.config.get_game_mechanic("recent_turns_to_keep", 5)
            current_summary = session.get("summary", "")

            should_summarize = (new_round % summarization_interval) == 0 and len(turns) > recent_turns_to_keep

            if should_summarize:
                logger.info(f"Round {new_round}: Generating summary")
                old_turns = turns[:-recent_turns_to_keep] if len(turns) > recent_turns_to_keep else []
                recent_turns = turns[-recent_turns_to_keep:] if len(turns) > recent_turns_to_keep else turns

                if old_turns:
                    old_history_text = self.history_builder.turns_to_history_text(old_turns)
                    new_summary = await self.history_builder.summarize_history([old_history_text])
                    current_summary = f"{current_summary}\n\n{new_summary}" if current_summary else new_summary

                history_text = self.history_builder.turns_to_history_text(recent_turns, summary=current_summary)
            else:
                history_text = self.history_builder.turns_to_history_text(turns, summary=current_summary)

            character_registry = session.get("character_registry", [])

            wildcard = self.config.get_random_wildcard()

            narrator_prompt = self.config.get_prompt(
                "narrator",
                history=history_text,
                wildcard=wildcard,
                character_registry=character_registry
            )

            narrator_model = self.config.get_model("narrator")
            narrator_params = self.config.get_sampling_params("narrator")

            response_text, fun_nugget = await asyncio.gather(
                self.llm.generate_text(
                    prompt=narrator_prompt,
                    model=narrator_model,
                    sampling_params=narrator_params,
                    json_mode=True,
                ),
                self.story_gen.generate_fun_nugget(history_text),
            )

            response_data = json.loads(response_text)
            story_text = response_data.get("story_text", "")

            main_choices = [
                response_data.get("choice_1", "").strip(),
                response_data.get("choice_2", "").strip(),
                response_data.get("choice_3", "").strip(),
            ]

            logger.info(f"Extracted 3 choices: {[c[:30] + '...' for c in main_choices]}")

            new_characters = self.char_manager.extract_characters_from_response(
                response_data=response_data,
                current_round=new_round
            )

            updated_registry = self.char_manager.merge_characters(
                existing_registry=character_registry,
                new_characters=new_characters,
                current_round=new_round
            )

            is_safe = await self.story_gen.validate_safety(story_text)
            if not is_safe:
                logger.warning(f"Unsafe content detected in session {session_id}")
                story_text = "Oh, das war eine interessante Wendung! Aber lass uns eine andere Richtung einschlagen."

            choices = main_choices

            new_turn = {
                "round": new_round,
                "choice_made": choice_text,
                "story_text": story_text,
                "choices": choices,
                "image_url": None,
                "fun_nugget": fun_nugget,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            }

            update_doc = {
                "$push": {"turns": new_turn},
                "$set": {
                    "character_registry": updated_registry,
                    "round": new_round,
                    "generation_status": "ready",
                    "lastUpdated": datetime.utcnow(),
                }
            }

            if should_summarize and current_summary:
                update_doc["$set"]["summary"] = current_summary

            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                update_doc,
            )

            style_guide = session.get("style_guide", "")
            char_names = [c["name"] for c in new_characters if "name" in c]

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

            choices_history = [t.get("choice_made") for t in turns if t.get("choice_made")]

            return AdventureStepResponse(
                story_text=story_text,
                image_url=None,
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

    async def generate_first_story(self, session_id: str):
        """Background task to generate the first story for a session.

        Args:
            session_id: The session ID to generate story for
        """
        try:
            logger.info(f"Starting background story generation for session {session_id}")

            session = await self.session_mgr.load_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return

            await self.start_adventure(
                user_id=session["userId"],
                character_name=session["character_name"],
                character_description=session["character_description"],
                story_theme=session["story_theme"],
            )

            logger.info(f"Successfully generated story for session {session_id}")

        except Exception as e:
            logger.error(f"Error generating story for session {session_id}: {e}")
            await self.session_mgr.mark_error(session_id, str(e))

    async def process_turn_async(self, session_id: str, choice_text: str):
        """Background task to process a turn asynchronously.

        Args:
            session_id: The game session ID
            choice_text: The user's choice text
        """
        try:
            logger.info(f"Starting background turn processing for session {session_id}")

            await self.process_turn(
                session_id=session_id,
                choice_text=choice_text,
            )

            logger.info(f"Successfully generated turn for session {session_id}")

        except Exception as e:
            logger.error(f"Error generating turn for session {session_id}: {e}")
            await self.session_mgr.recover_incomplete_turns(session_id)
            await self.session_mgr.mark_error(session_id, str(e))


def get_game_engine() -> GameEngine:
    """Get an instance of the game engine."""
    return GameEngine()
