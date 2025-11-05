"""Centralized logging configuration for Märchenweber backend."""

import logging
import sys
from datetime import datetime


def setup_logger() -> logging.Logger:
    """Configure and return the global logger for the application.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("maerchenweber")

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console handler with detailed formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Format: timestamp - level - message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger() -> logging.Logger:
    """Get the global logger instance.

    Returns:
        Global logger instance
    """
    return logging.getLogger("maerchenweber")


# Initialize logger on module import
logger = setup_logger()
