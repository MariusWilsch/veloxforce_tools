"""OpenRouter Tools - A toolkit for working with OpenRouter and Langfuse APIs."""

__version__ = "0.3.1"

# Initialize logging
from openrouter_tools.core.logger import configure_logging

configure_logging()

# Initialize settings
from openrouter_tools.core.settings import get_settings

get_settings()  # Load settings on import

# Import services
from openrouter_tools.services.message_builder import MessageBuilder
from openrouter_tools.services.openrouter_service import OpenRouterService
from openrouter_tools.services.langfuse_service import LangfuseService

__all__ = ["MessageBuilder", "OpenRouterService", "LangfuseService"]
