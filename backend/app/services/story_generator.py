"""Story generation service for Märchenweber - handles narrator, validation, fun nuggets."""

import logging
from typing import Any

from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Handles story generation, validation, and fun facts."""

    def __init__(self):
        """Initialize the story generator."""
        self.config = get_config_loader()
        self.llm = get_llm_service()

    async def generate_style_guide(
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

    async def validate_safety(self, german_text: str) -> bool:
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

            return "SAFE" in response.upper()

        except Exception as e:
            logger.error(f"Safety validation error: {e}")
            return True

    async def generate_fun_nugget(self, current_story: str) -> str:
        """Generate a fun fact or teaser related to the current story.

        Args:
            current_story: The current story context

        Returns:
            Fun nugget text (1 sentence)
        """
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


def get_story_generator() -> StoryGenerator:
    """Get an instance of the story generator."""
    return StoryGenerator()
