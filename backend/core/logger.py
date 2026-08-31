"""
Application Logger

Configures Loguru for structured logging across the application.
Logs are written to both the console and rotating log files.
"""

import sys

from loguru import logger

from core.constants import (
    LOG_DIR,
    LOG_FILE_NAME,
    LOG_RETENTION,
    LOG_ROTATION,
)

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Remove default logger
logger.remove()

# Console logger
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

# File logger
logger.add(
    LOG_DIR / LOG_FILE_NAME,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression="zip",
    level="DEBUG",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)

__all__ = ["logger"]