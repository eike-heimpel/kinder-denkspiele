"""Utility functions for timing and error tracking."""

import time
import logging
from typing import Dict, List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class StepTimer:
    """Track timing for each step in the pipeline."""

    def __init__(self):
        self.steps: List[Dict[str, float]] = []
        self.current_step: Optional[str] = None
        self.step_start: Optional[float] = None

    @contextmanager
    def step(self, name: str):
        """Context manager to time a step."""
        self.current_step = name
        self.step_start = time.time()
        logger.info(f"[STEP START] {name}")

        try:
            yield
        except Exception as e:
            duration = time.time() - self.step_start
            self.steps.append({
                "name": name,
                "duration_ms": round(duration * 1000, 2),
                "status": "error",
                "error": str(e)
            })
            logger.error(f"[STEP ERROR] {name} failed after {duration:.2f}s: {e}")
            raise
        else:
            duration = time.time() - self.step_start
            self.steps.append({
                "name": name,
                "duration_ms": round(duration * 1000, 2),
                "status": "success"
            })
            logger.info(f"[STEP COMPLETE] {name} ({duration:.2f}s)")

    def get_summary(self) -> Dict:
        """Get timing summary."""
        total_ms = sum(s["duration_ms"] for s in self.steps)
        return {
            "steps": self.steps,
            "total_ms": round(total_ms, 2),
            "step_count": len(self.steps)
        }
