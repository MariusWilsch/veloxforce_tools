"""
Basic Rich logging configuration for OpenRouter Tools.
"""

import logging
import os
from rich.logging import RichHandler
from rich.console import Console

# Import settings using relative import to avoid circular imports
from openrouter_tools.core.settings import get_settings


def configure_logging():
    """
    Configure the logging system with a basic Rich handler.

    Args:
        level: The base log level (default: INFO)
    """
    console = Console()
    logging.basicConfig(
        level=get_settings().LOG_LEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
    )


def get_logger(name):
    """
    Get a configured logger for the specified name.

    Args:
        name: The name for the logger, typically __name__

    Returns:
        A configured Logger instance
    """
    return logging.getLogger(name)
