"""Veloxforce Tools - A toolkit for working with OpenRouter, Langfuse, and Email APIs."""

__version__ = "0.4.1"

# Initialize logging
from veloxforce_tools.core.logger import configure_logging

configure_logging()

# Initialize settings
from veloxforce_tools.services.message_builder import MessageBuilder
from veloxforce_tools.services.openrouter_service import OpenRouterService
from veloxforce_tools.services.langfuse_service import LangfuseService
from veloxforce_tools.services.email_service import EmailService

__all__ = ["MessageBuilder", "OpenRouterService", "LangfuseService", "EmailService"]
