import json
import httpx
import base64
import re
from typing import Optional, Dict, List, Type, TypeVar, Any, Union, Literal
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from langfuse.openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from veloxforce_tools.core.logger import get_logger
from veloxforce_tools.core.settings import get_settings

# Get a configured logger
logger = get_logger(__name__)

# Get settings and max retries
settings = get_settings()
MAX_RETRIES = settings.MAX_RETRIES

T = TypeVar("T", bound=BaseModel)


class OpenRouterService:
    """
    Service for interacting with OpenRouter API using the OpenAI SDK.

    This service provides methods for:
    - Chat completions
    - Structured output generation with optional image URLs
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        """
        Initialize the OpenRouter service.

        Args:
            api_key: OpenRouter API key (if None, uses OPENROUTER_API_KEY from settings)
            base_url: OpenRouter API base URL
            site_url: Site URL for HTTP-Referer header
            site_name: Site name for X-Title header
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Provide it directly or set OPENROUTER_API_KEY in environment variables or .env file."
            )

        self.base_url = base_url
        self.site_url = site_url
        self.site_name = site_name
        self.client = self._create_client()

    def _create_client(self) -> AsyncOpenAI:
        """
        Create an AsyncOpenAI client configured for OpenRouter.

        Returns:
            AsyncOpenAI client instance
        """
        extra_headers = {}
        if self.site_url:
            extra_headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            extra_headers["X-Title"] = self.site_name

        return AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers=extra_headers,
        )

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a chat completion using OpenRouter.

        Args:
            messages: List of message dictionaries ready for the API
            model: Model identifier (e.g., "openai/gpt-4o", "anthropic/claude-3-haiku")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            str: The text response from the model

        Raises:
            ValueError: If the API key is missing
            httpx.HTTPStatusError: If the API request fails
            Exception: For other errors

        Examples:
            ```python
            service = OpenRouterService(api_key="your-api-key")
            messages = await MessageBuilder.build_messages(
                prompt="What is the capital of France?",
                system_prompt="Be concise."
            )
            result = await service.chat_completion(
                messages=messages,
                model="anthropic/claude-3-haiku"
            )
            print(result)  # "Paris."
            ```
        """
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info(f"Chat completion response: {response}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def structured_output(
        self,
        messages: List[Dict[str, Any]],
        schema_model: Type[T],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """
        Generate a structured output following a Pydantic model schema.

        Args:
            messages: List of message dictionaries ready for the API
            schema_model: Pydantic model class defining the output structure
            model: Model identifier (must support structured outputs)
            **kwargs: Additional parameters to pass to the API

        Returns:
            T: Instance of the provided Pydantic model

        Raises:
            ValueError: If the API key is missing
            httpx.HTTPStatusError: If the API request fails
            Exception: For other errors

        Examples:
            ```python
            from pydantic import BaseModel

            class WeatherResponse(BaseModel):
                temperature: float
                conditions: str
                humidity: int

            service = OpenRouterService(api_key="your-api-key")
            messages = await MessageBuilder.build_messages(
                prompt="What's the weather in Paris?",
                system_prompt="Return structured data only."
            )
            result = await service.structured_output(
                messages=messages,
                schema_model=WeatherResponse,
                model="openai/gpt-4o"
            )
            print(f"Temperature: {result.temperature}°C")
            ```
        """
        # Get JSON schema from Pydantic model
        json_schema = schema_model.model_json_schema()

        # Configure response format for structured output
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_model.__name__,
                "strict": True,
                "schema": json_schema,
            },
        }

        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "response_format": response_format,
        }

        # Add any additional parameters
        payload.update(kwargs)

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(
            f"Calling OpenRouter with messages: \n|{json.dumps(messages, indent=2)}|"
        )

        # Make the request using httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )

                # Raise for HTTP errors
                response.raise_for_status()

                # Parse the response
                data = response.json()
                # Extract the content from the response
                content = data["choices"][0]["message"]["content"]
                # Create and return an instance of the schema_model
                logger.info(f"Structured output: \n|{content}|")
                return content
                # TODO: Use pydantic to validate the content
                # return schema_model.model_validate(content)

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error in structured output: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Error in structured output: {str(e)}")
            raise

    def extract_xml_tag(self, content: str, tag_name: str) -> str:
        """
        Extract text between XML tags from a string.

        Args:
            content: The string containing XML tags
            tag_name: The name of the XML tag to extract from

        Returns:
            str: The text between the opening and closing tags with strip() and lower() applied, or empty string if not found

        Examples:
            ```python
            service = OpenRouterService(api_key="your-api-key")
            content = "<response><answer>Paris</answer><confidence>High</confidence></response>"
            answer = service.extract_xml_tag(content, "answer")  # Returns "paris"
            confidence = service.extract_xml_tag(content, "confidence")  # Returns "high"
            ```
        """
        # Create the pattern to match opening and closing tags
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"

        # Use re.DOTALL to make . match newlines as well
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # Return the text between the tags (group 1)
            return match.group(1).strip().lower()
        else:
            logger.warning(f"Tag '{tag_name}' not found in content")
            return ""
