import os
from typing import Dict, Any, Optional
from langfuse import Langfuse

from veloxforce_tools.core.logger import get_logger
from veloxforce_tools.core.settings import get_settings

# Get a configured logger
logger = get_logger(__name__)

# Get settings
settings = get_settings()


class LangfuseService:
    """
    Service for managing prompts with Langfuse.

    This service provides methods for:
    - Retrieving text prompts
    - Retrieving chat prompts
    - Compiling prompts with variables
    """

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
    ):
        """
        Initialize the Langfuse service.

        Args:
            public_key: Langfuse public key (if None, uses LANGFUSE_PUBLIC_KEY env var)
            secret_key: Langfuse secret key (if None, uses LANGFUSE_SECRET_KEY env var)
            host: Optional Langfuse host URL
        """
        # Set environment variables if keys are provided
        if public_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
        if secret_key:
            os.environ["LANGFUSE_SECRET_KEY"] = secret_key
        if host:
            os.environ["LANGFUSE_HOST"] = host

        # Initialize Langfuse client
        self.langfuse = Langfuse()
        logger.debug("Langfuse service initialized")

    def get_text_prompt(self, prompt_name: str, label: str = "latest") -> Any:
        """
        Get a text prompt from Langfuse by name and label.

        Args:
            prompt_name: Name of the prompt in Langfuse
            label: Label of the prompt version (default: "latest")

        Returns:
            The prompt object
        """
        try:
            prompt = self.langfuse.get_prompt(name=prompt_name, label=label)
            logger.debug(f"Retrieved text prompt '{prompt_name}' with label '{label}'")
            return prompt
        except Exception as e:
            logger.error(f"Error retrieving text prompt '{prompt_name}': {e}")
            return None

    def get_chat_prompt(self, prompt_name: str, label: str = "latest") -> Any:
        """
        Get a chat prompt from Langfuse by name and label.

        Args:
            prompt_name: Name of the prompt in Langfuse
            label: Label of the prompt version (default: "latest")

        Returns:
            The prompt object
        """
        try:
            prompt = self.langfuse.get_prompt(
                name=prompt_name, label=label, type="chat"
            )
            logger.debug(f"Retrieved chat prompt '{prompt_name}' with label '{label}'")
            return prompt
        except Exception as e:
            logger.error(f"Error retrieving chat prompt '{prompt_name}': {e}")
            return None

    def compile_prompt(self, prompt: Any, variables: Dict[str, Any]) -> Any:
        """
        Compile a prompt with variables.

        Args:
            prompt: The prompt object from Langfuse
            variables: Dictionary of variables to insert into the prompt

        Returns:
            The compiled prompt
        """
        try:
            compiled_prompt = prompt.compile(**variables)
            logger.debug(f"Compiled prompt with variables: {variables}")
            return compiled_prompt
        except Exception as e:
            logger.error(f"Error compiling prompt: {e}")
            return None
