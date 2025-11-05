"""Async image generation service with choice-based prompts and RNG variance."""

import asyncio
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.database import get_database
from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service
from app.exceptions import ImageGenerationError, LLMError
from app.logger import logger
from bson import ObjectId


class ImageGenerator:
    """Handles async image generation with choice-based prompts and scene-aware variance."""

    def __init__(self):
        self.config = get_config_loader()
        self.llm = get_llm_service()
        self.db = get_database()
        self.collection = self.db["gamesessions"]

    def get_random_variance(self, intensity_level: int) -> Dict[str, str]:
        """Select random variance parameters based on scene intensity.

        Args:
            intensity_level: Scene intensity (1=calm, 5=exciting)

        Returns:
            Dict with perspective, lighting, framing
        """
        variance_config = self.config.get_image_variance()

        # Select perspective randomly
        perspective = random.choice(variance_config["perspectives"])

        # Select lighting based on intensity
        if intensity_level <= 2:
            lighting_pool = variance_config["lighting_by_intensity"]["low"]
        elif intensity_level <= 3:
            lighting_pool = variance_config["lighting_by_intensity"]["medium"]
        else:
            lighting_pool = variance_config["lighting_by_intensity"]["high"]

        lighting = random.choice(lighting_pool)

        # Select framing randomly
        framing = random.choice(variance_config["framing"])

        return {
            "perspective": perspective,
            "lighting": lighting,
            "framing": framing
        }

    async def generate_choice_based_image(
        self,
        session_id: str,
        choice_made: str,
        story_text: str,
        style_guide: str,
        characters_in_scene: List[str],
        character_descriptions: Dict[str, str],
        current_round: int
    ):
        """Generate image asynchronously in background.

        This is the main entry point for async image generation. It:
        1. Marks image as "generating" in MongoDB
        2. Generates choice-specific prompt
        3. Applies RNG variance
        4. Generates image
        5. Marks as "ready" or "failed"

        Args:
            session_id: Game session ID
            choice_made: User's choice text
            story_text: Current story segment
            style_guide: Visual style guide
            characters_in_scene: List of character names in scene
            character_descriptions: Dict mapping character name to description
            current_round: Current round number
        """
        try:
            logger.info(f"🎨 [IMAGE GEN START] Session: {session_id}, Round: {current_round}")
            start_time = datetime.utcnow()

            # Step 1: Mark as generating
            logger.info(f"[STEP 1/6] Marking session as 'generating' in DB...")
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "pending_image": {
                            "status": "generating",
                            "round": current_round,
                            "image_url": None,
                            "started_at": start_time,
                            "completed_at": None,
                            "error": None
                        }
                    }
                }
            )
            logger.info(f"✅ [STEP 1/6] DB updated successfully")

            # Step 2: Generate choice-specific prompt
            logger.info(f"[STEP 2/6] Generating choice-specific prompt...")
            logger.info(f"  - Choice: {choice_made[:60]}...")
            logger.info(f"  - Characters in scene: {characters_in_scene}")
            choice_prompt_text = await self._generate_choice_prompt(
                choice_made=choice_made,
                story_text=story_text,
                characters_in_scene=characters_in_scene,
                character_descriptions=character_descriptions
            )
            logger.info(f"✅ [STEP 2/6] Choice prompt generated: {choice_prompt_text[:100]}...")

            # Step 3: Analyze scene for intensity (for variance)
            logger.info(f"[STEP 3/6] Analyzing scene intensity...")
            intensity = await self._analyze_scene_intensity(story_text)
            logger.info(f"✅ [STEP 3/6] Scene intensity: {intensity}/5")

            # Step 4: Get random variance parameters
            logger.info(f"[STEP 4/6] Generating variance parameters...")
            variance = self.get_random_variance(intensity)
            logger.info(f"✅ [STEP 4/6] Variance: perspective={variance['perspective']}, lighting={variance['lighting']}, framing={variance['framing']}")

            # Step 5: Build final prompt
            logger.info(f"[STEP 5/6] Building final image prompt...")
            final_prompt = self._build_final_prompt(
                choice_prompt=choice_prompt_text,
                style_guide=style_guide,
                character_descriptions=character_descriptions,
                variance=variance
            )
            logger.info(f"✅ [STEP 5/6] Final prompt built ({len(final_prompt)} chars)")

            # Step 6: Generate image (NO previous image input!)
            logger.info(f"[STEP 6/6] Calling LLM to generate image...")
            image_model = self.config.get_model("image_generator")
            logger.info(f"  - Model: {image_model}")
            logger.info(f"  - Aspect ratio: 4:3")
            image_url = await self.llm.generate_image(
                prompt=final_prompt,
                model=image_model,
                aspect_ratio="4:3",
                previous_image_url=None,  # No image feeding!
                style_description=None  # Style comes from text only
            )
            logger.info(f"✅ [STEP 6/6] Image generated successfully")

            # Step 7: Update turn's image_url atomically
            logger.info(f"[STEP 7/7] Saving image URL to DB...")
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = await self.collection.update_one(
                {"_id": ObjectId(session_id), "turns.round": current_round},
                {
                    "$set": {
                        "turns.$.image_url": image_url,
                        "pending_image": {
                            "status": "ready",
                            "round": current_round,
                            "image_url": image_url,
                            "completed_at": end_time,
                            "error": None
                        }
                    }
                }
            )

            if result.modified_count == 0:
                logger.warning(
                    f"⚠️ [STEP 7/7] Image generated but turn not found for round {current_round}. "
                    f"Turn may have been removed during error recovery."
                )
            else:
                logger.info(f"✅ [STEP 7/7] Image URL saved to DB successfully")

            logger.info(f"🎉 [IMAGE GEN COMPLETE] Session: {session_id}, Round: {current_round}, Duration: {duration:.2f}s")

        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__

            logger.error(
                f"Image generation failed for session {session_id}",
                extra={
                    "session_id": session_id,
                    "round": current_round,
                    "error_type": error_type,
                    "error_message": error_message
                },
                exc_info=True
            )

            # Mark as failed with detailed error info
            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "pending_image": {
                            "status": "failed",
                            "round": current_round,
                            "image_url": None,
                            "started_at": datetime.utcnow(),
                            "completed_at": datetime.utcnow(),
                            "error": error_message,
                            "error_type": error_type
                        }
                    }
                }
            )

    async def _generate_choice_prompt(
        self,
        choice_made: str,
        story_text: str,
        characters_in_scene: List[str],
        character_descriptions: Dict[str, str]
    ) -> str:
        """Generate choice-specific image prompt.

        Args:
            choice_made: User's choice
            story_text: Current story
            characters_in_scene: Character names in scene
            character_descriptions: Character visual descriptions

        Returns:
            Choice-specific image prompt (English, 2-3 sentences)

        Raises:
            LLMError: If prompt generation fails
        """
        try:
            # Build character info for prompt
            char_info = []
            for name in characters_in_scene:
                desc = character_descriptions.get(name, "")
                if desc:
                    char_info.append({"name": name, "description": desc})

            prompt = self.config.get_prompt(
                "choice_image_generator",
                choice_made=choice_made,
                story_text=story_text,
                characters_in_scene=char_info
            )

            model = self.config.get_model("choice_image_generator")
            params = self.config.get_sampling_params("choice_image_generator")

            result = await self.llm.generate_text(
                prompt=prompt,
                model=model,
                sampling_params=params
            )

            if not result or len(result.strip()) < 10:
                raise LLMError(
                    message="Choice image prompt too short or empty",
                    model=model,
                    prompt_length=len(prompt)
                )

            logger.info(f"Generated choice prompt: {result[:100]}...")
            return result.strip()

        except Exception as e:
            if isinstance(e, LLMError):
                raise
            raise LLMError(
                message=f"Failed to generate choice image prompt: {str(e)}",
                model=model,
                prompt_length=len(prompt),
                original_error=e
            )

    async def _analyze_scene_intensity(self, story_text: str) -> int:
        """Analyze scene for intensity level (1-5).

        Args:
            story_text: Story segment to analyze

        Returns:
            Intensity level (1=calm, 5=exciting)
        """
        try:
            prompt = self.config.get_prompt(
                "scene_intensity_analyzer",
                story_segment=story_text[:500]
            )

            model = self.config.get_model("scene_analyzer")
            params = self.config.get_sampling_params("scene_analyzer")

            result = await self.llm.generate_text(
                prompt=prompt,
                model=model,
                sampling_params=params,
                json_mode=True
            )

            import json

            # Clean up result (remove markdown code blocks if present)
            result_clean = result.strip()
            if result_clean.startswith("```json"):
                result_clean = result_clean[7:]
            if result_clean.startswith("```"):
                result_clean = result_clean[3:]
            if result_clean.endswith("```"):
                result_clean = result_clean[:-3]
            result_clean = result_clean.strip()

            data = json.loads(result_clean)
            intensity = data.get("intensity_level", 3)

            # Validate intensity is in range
            if not isinstance(intensity, int) or intensity < 1 or intensity > 5:
                logger.warning(f"Invalid intensity value: {intensity}, using default 3")
                return 3

            return intensity

        except json.JSONDecodeError as e:
            logger.warning(f"Scene analysis JSON parse error: {e}, response was: {result[:200]}, using default intensity=3")
            return 3
        except Exception as e:
            logger.warning(f"Scene analysis failed: {e}, using default intensity=3")
            return 3

    def _build_final_prompt(
        self,
        choice_prompt: str,
        style_guide: str,
        character_descriptions: Dict[str, str],
        variance: Dict[str, str]
    ) -> str:
        """Build final image generation prompt.

        Args:
            choice_prompt: Choice-specific action description
            style_guide: Visual style guide
            character_descriptions: Character visual info
            variance: RNG variance parameters

        Returns:
            Final prompt for image generation
        """
        # Format character descriptions
        char_lines = []
        missing_descriptions = []

        for name, desc in character_descriptions.items():
            if desc:
                char_lines.append(f"{name}: {desc}")
            else:
                missing_descriptions.append(name)
                logger.warning(f"⚠️ Character '{name}' has NO description for image generation!")

        char_text = ", ".join(char_lines) if char_lines else "no specific character descriptions"

        # Log character info
        if char_lines:
            logger.info(f"✅ Characters with descriptions: {len(char_lines)}")
            for line in char_lines:
                logger.info(f"  - {line}")

        if missing_descriptions:
            logger.error(
                f"❌ CONSISTENCY PROBLEM: {len(missing_descriptions)} character(s) "
                f"without descriptions: {', '.join(missing_descriptions)}"
            )

        # Build final prompt
        prompt_parts = [
            choice_prompt,
            f"\nStyle: {style_guide}",
            f"\nCharacters: {char_text}",
            f"\nPerspective: {variance['perspective']}",
            f"\nLighting: {variance['lighting']}",
            f"\nFraming: {variance['framing']}"
        ]

        final_prompt = " ".join(prompt_parts)
        logger.info(f"📝 Final image prompt length: {len(final_prompt)} characters")

        return final_prompt


def get_image_generator() -> ImageGenerator:
    """Get an instance of the image generator.

    Returns:
        ImageGenerator instance
    """
    return ImageGenerator()
