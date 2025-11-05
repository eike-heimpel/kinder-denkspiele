"""Session management service - handles session CRUD and recovery."""

from app.logger import logger
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId

from app.database import get_database



class SessionManager:
    """Handles session creation, loading, and error recovery."""

    def __init__(self):
        """Initialize the session manager."""
        self.db = get_database()
        self.collection = self.db["gamesessions"]

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
            "generation_status": "generating",
            "turns": [],
            "summary": "",
            "score": 0,
            "round": 0,
            "createdAt": datetime.utcnow(),
            "lastUpdated": datetime.utcnow(),
            "style_guide": "",
            "character_registry": [],
            "pending_image": None
        }

        result = await self.collection.insert_one(session_doc)
        session_id = str(result.inserted_id)
        logger.info(f"Created session {session_id} with status 'generating'")
        return session_id

    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session from the database.

        Args:
            session_id: The session ID to load

        Returns:
            Session document or None if not found

        Raises:
            ValueError: If session uses old format without turns[]
        """
        session = await self.collection.find_one({"_id": ObjectId(session_id)})

        if not session:
            return None

        if "turns" not in session:
            raise ValueError(
                f"Session {session_id} uses outdated format. "
                "Please manually migrate in MongoDB or start a new story."
            )

        return session

    async def recover_incomplete_turns(self, session_id: str) -> bool:
        """Remove any incomplete turns on session load for error recovery.

        Args:
            session_id: The session ID to recover

        Returns:
            True if recovery was needed, False otherwise
        """
        session = await self.collection.find_one({"_id": ObjectId(session_id)})
        if not session:
            return False

        turns = session.get("turns", [])
        if not turns:
            return False

        complete_turns = [t for t in turns if t.get("completed_at")]

        if len(complete_turns) < len(turns):
            logger.warning(
                f"Session {session_id}: Recovering from incomplete state. "
                f"Removing {len(turns) - len(complete_turns)} incomplete turn(s)"
            )

            await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "turns": complete_turns,
                        "generation_status": "ready" if complete_turns else "error",
                        "round": len(complete_turns),
                        "lastUpdated": datetime.utcnow()
                    }
                }
            )
            return True

        return False

    async def mark_error(self, session_id: str, error_message: str):
        """Mark a session as having an error.

        Args:
            session_id: The session ID
            error_message: Error message to store
        """
        await self.collection.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "generation_status": "error",
                    "generation_error": error_message,
                    "lastUpdated": datetime.utcnow()
                }
            }
        )


def get_session_manager() -> SessionManager:
    """Get an instance of the session manager."""
    return SessionManager()
