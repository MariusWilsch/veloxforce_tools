import json
import copy
import re
from typing import List, Optional, Dict, Any

from veloxforce_tools.schemas.openrouter import (
    Message,
    TextContent,
    ImageUrlContent,
    FileContent,
)

from veloxforce_tools.core.logger import get_logger

# Get a configured logger
logger = get_logger(__name__)


class MessageBuilder:
    """
    Helper class for building OpenRouter API messages.

    This class provides methods for creating different types of messages
    with various content types (text, images, files).
    """

    @staticmethod
    def text_message(role: str, text: str) -> Message:
        """Create a simple text message."""
        return Message(role=role, content=text)

    @staticmethod
    def system_message(text: str) -> Message:
        """Create a system message."""
        return Message(role="system", content=text)

    @staticmethod
    def user_message(text: str) -> Message:
        """Create a user message."""
        return Message(role="user", content=text)

    @staticmethod
    def assistant_message(text: str) -> Message:
        """Create an assistant message."""
        return Message(role="assistant", content=text)

    @staticmethod
    def content_message(
        role: str,
        text: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        pdf_data: Optional[List[str]] = None,
    ) -> Message:
        """
        Create a message with text and optional images and files.

        Args:
            role: The role of the message sender ("user", "assistant", "system")
            text: The text content of the message
            image_urls: Optional list of image URLs to include
            pdf_data: Optional list of PDF data to include (must be base64 encoded data URLs)

        Returns:
            A Message object with the specified content

        Raises:
            ValueError: If any pdf_data item is a direct PDF URL instead of a base64 encoded data URL
        """
        content_items = [TextContent(text=text)]

        if image_urls:
            for image_url in image_urls:
                content_items.append(ImageUrlContent(image_url={"url": image_url}))

        if pdf_data:
            if isinstance(pdf_data, str):
                pdf_data = [pdf_data]  # Convert to list if single string
            for idx, file_url in enumerate(pdf_data):
                # Check if this is a direct PDF URL (not supported by OpenRouter)
                if file_url.startswith("http") and file_url.lower().endswith(".pdf"):
                    raise ValueError(
                        "Direct PDF URLs are not supported by OpenRouter. "
                        "PDFs must be fetched and encoded to base64 first."
                    )
                content_items.append(
                    FileContent(
                        file={"filename": f"document_{idx}.pdf", "file_data": file_url}
                    )
                )

        return Message(role=role, content=content_items)

    @staticmethod
    def _log_messages_redacted(messages: List[Message]) -> None:
        """
        Log messages with redacted base64 content for better readability.

        Args:
            messages: List of Message objects to log
        """
        # Create a deep copy to avoid modifying the original messages
        redacted_messages = copy.deepcopy(messages)

        # Redact base64 content in each message
        for message in redacted_messages:
            if isinstance(message.content, list):
                for item in message.content:
                    if hasattr(item, "file") and hasattr(item.file, "file_data"):
                        # Check if it's a base64 data URL
                        if (
                            isinstance(item.file.file_data, str)
                            and "base64" in item.file.file_data
                        ):
                            # Extract the MIME type if present
                            mime_match = re.match(
                                r"data:(.*?);base64,", item.file.file_data
                            )
                            mime_type = mime_match.group(1) if mime_match else "unknown"
                            # Replace the base64 data with a placeholder
                            item.file.file_data = f"[BASE64 {mime_type} DATA REDACTED]"

        # Log the redacted messages
        logger.debug(
            f"Messages (with base64 content redacted): {json.dumps([m.model_dump() for m in redacted_messages], indent=2)}"
        )

    @staticmethod
    async def build_messages(
        prompt: str,
        system_prompt: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        pdf_data: Optional[List[str] | str] = None,
    ) -> List[Dict]:
        """
        Build a list of messages from the given parameters.

        Args:
            prompt: Text prompt for the model
            system_prompt: Optional system prompt to add before the user message
            image_urls: Optional list of image URLs to include
            pdf_data: Optional list of PDF data to include

        Returns:
            List of message dictionaries ready for the API
        """
        messages = []

        # Add system message if provided
        if system_prompt:
            messages.append(MessageBuilder.system_message(system_prompt))

        # Create user message based on content types
        user_message = MessageBuilder.user_message(prompt)

        # Add images if provided
        if image_urls:
            user_message = MessageBuilder.content_message(
                "user", prompt, image_urls=image_urls
            )

        # Add PDFs if provided
        if pdf_data:
            user_message = MessageBuilder.content_message(
                "user", prompt, pdf_data=pdf_data
            )

        messages.append(user_message)

        # Log messages with redacted base64 content
        MessageBuilder._log_messages_redacted(messages)

        # Convert Message objects to dictionaries
        return [message.model_dump() for message in messages]
