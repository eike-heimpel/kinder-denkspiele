"""History formatting service - converts turns to LLM context."""

from app.logger import logger
from typing import Dict, Any, List

from app.services.config_loader import get_config_loader
from app.services.llm_service import get_llm_service



class HistoryBuilder:
    """Handles history formatting and summarization for LLM context."""

    def __init__(self):
        """Initialize the history builder."""
        self.config = get_config_loader()
        self.llm = get_llm_service()

    def turns_to_history_text(self, turns: List[Dict[str, Any]], summary: str = "") -> str:
        """Convert turns array to history text for LLM context.

        Args:
            turns: List of turn objects from MongoDB
            summary: Optional summary of old turns

        Returns:
            Formatted history text for LLM prompts
        """
        lines = []
        for turn in turns:
            choice_made = turn.get("choice_made")
            if choice_made:
                lines.append(f"[Wahl]: {choice_made}")
            story_text = turn.get("story_text", "")
            if story_text:
                lines.append(story_text)

        history_text = "\n\n".join(lines)

        if summary:
            history_text = f"{summary}\n\n---\n\n{history_text}"

        return history_text

    async def summarize_history(self, history: List[str]) -> str:
        """Summarize story history to keep context manageable.

        Args:
            history: List of history segments to summarize

        Returns:
            Summarized history text
        """
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


def get_history_builder() -> HistoryBuilder:
    """Get an instance of the history builder."""
    return HistoryBuilder()
