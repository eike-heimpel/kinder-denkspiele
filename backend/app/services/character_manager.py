"""Character registry management for consistent character appearances."""

from app.logger import logger
from typing import List, Dict, Any
from datetime import datetime



class CharacterManager:
    """Manages the character registry for persistent character descriptions."""

    @staticmethod
    def extract_characters_from_response(
        response_data: Dict[str, Any],
        current_round: int
    ) -> List[Dict[str, Any]]:
        """Extract character information from narrator response.

        Args:
            response_data: Parsed JSON response from narrator
            current_round: Current round number

        Returns:
            List of character dicts with name, description, first_seen_round, last_seen_round
        """
        characters_in_scene = response_data.get("characters_in_scene", [])
        extracted = []

        for char in characters_in_scene:
            name = char.get("name")
            description = char.get("description")

            if not name:
                continue

            char_doc = {
                "name": name,
                "first_seen_round": current_round,
                "last_seen_round": current_round,
            }

            # Only add description if provided (new character)
            if description:
                char_doc["description"] = description

            extracted.append(char_doc)

        return extracted

    @staticmethod
    def merge_characters(
        existing_registry: List[Dict[str, Any]],
        new_characters: List[Dict[str, Any]],
        current_round: int
    ) -> List[Dict[str, Any]]:
        """Merge new characters into existing registry.

        - Existing characters: Update last_seen_round
        - New characters: Add to registry with description

        Args:
            existing_registry: Current character registry from MongoDB
            new_characters: Characters extracted from narrator response
            current_round: Current round number

        Returns:
            Updated character registry
        """
        # Build a lookup map: name → character doc
        registry_map = {char["name"]: char for char in existing_registry}

        for new_char in new_characters:
            name = new_char["name"]

            if name in registry_map:
                # Existing character - update last_seen_round
                registry_map[name]["last_seen_round"] = current_round
                logger.info(f"Updated existing character: {name} (last seen: round {current_round})")
            else:
                # New character - add to registry
                if "description" not in new_char:
                    logger.warning(f"New character '{name}' without description - skipping")
                    continue

                registry_map[name] = new_char
                logger.info(f"Added new character: {name} - {new_char['description']}")

        return list(registry_map.values())

    @staticmethod
    def get_character_descriptions(
        character_registry: List[Dict[str, Any]],
        character_names: List[str]
    ) -> Dict[str, str]:
        """Get descriptions for specific characters.

        Args:
            character_registry: Full character registry
            character_names: Names of characters to retrieve

        Returns:
            Dict mapping character name to description
        """
        # Build full registry map (include all characters, even without descriptions)
        registry_map = {}
        for char in character_registry:
            name = char.get("name")
            if name:
                registry_map[name] = char.get("description", "")

        # Build result dict and log warnings for missing descriptions
        result = {}
        for name in character_names:
            description = registry_map.get(name, "")
            result[name] = description

            if not description:
                logger.warning(
                    f"Character '{name}' requested but has no description in registry. "
                    f"This will cause visual inconsistency!"
                )

        return result

    @staticmethod
    def format_for_prompt(character_registry: List[Dict[str, Any]]) -> str:
        """Format character registry for inclusion in prompts.

        Args:
            character_registry: Full character registry

        Returns:
            Formatted string for prompt injection
        """
        if not character_registry:
            return ""

        lines = []
        for char in character_registry:
            name = char["name"]
            description = char.get("description", "")
            if description:
                lines.append(f"- {name}: {description}")

        return "\n".join(lines)


def get_character_manager() -> CharacterManager:
    """Get an instance of the character manager.

    Returns:
        CharacterManager instance
    """
    return CharacterManager()
