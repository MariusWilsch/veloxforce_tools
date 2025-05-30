import json
import re
from typing import Optional, Dict, List, Type, TypeVar, Any

import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

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
    Service for interacting with OpenRouter API.

    This service provides methods for:
    - Chat completions (using HTTPX directly)
    - Structured output generation with optional image URLs
    """

    # Type annotations for instance attributes
    api_key: str
    helicone_api_key: str
    project_id: Optional[str]
    base_url: str

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        helicone_api_key: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize the OpenRouter service.

        Args:
            openrouter_api_key: OpenRouter API key (if None, uses OPENROUTER_API_KEY env var)
            helicone_api_key: Helicone API key (if None, uses HELICONE_API_KEY env var)
            project_id: Project ID for Helicone tracking (typically project name)
        """
        settings = get_settings()
        self.api_key = openrouter_api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Provide it directly or set OPENROUTER_API_KEY in environment variables or .env file."
            )

        self.helicone_api_key = helicone_api_key or settings.HELICONE_API_KEY
        if not self.helicone_api_key:
            raise ValueError(
                "Helicone API key is required. Provide it directly or set HELICONE_API_KEY in environment variables or .env file."
            )

        # Store project ID for Helicone tracking
        self.project_id = project_id

        # Use the direct OpenRouter API URL
        self.base_url = "https://openrouter.helicone.ai/api/v1"

    async def _make_api_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Make an API request to OpenRouter.

        Args:
            endpoint: API endpoint (e.g., "chat/completions")
            payload: Request payload

        Returns:
            Dict[str, Any]: API response

        Raises:
            httpx.HTTPStatusError: If the API request fails
            Exception: For other errors
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Helicone-Auth": f"Bearer {self.helicone_api_key}",
            "Content-Type": "application/json",
        }

        # Add project ID for Helicone tracking if provided
        if self.project_id:
            headers["Helicone-Property-Project"] = self.project_id

        logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{endpoint}",
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )

                # Raise for HTTP errors
                response.raise_for_status()

                # Parse the response
                data = response.json()
                logger.debug(f"API response: {json.dumps(data, indent=2)}")
                return data
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error in API request: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Error in API request: {str(e)}")
            raise

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
            service = OpenRouterService(
                openrouter_api_key="your-api-key",
                project_id="my-project-name"
            )
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
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        logger.info(f"Calling OpenRouter chat completion API with model {model}")

        data = await self._make_api_request("chat/completions", payload)
        return data["choices"][0]["message"]["content"]

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

            service = OpenRouterService(
                openrouter_api_key="your-api-key",
                project_id="weather-app"
            )
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

        logger.info(f"Calling OpenRouter structured output API with model {model}")

        data = await self._make_api_request("chat/completions", payload)
        content = data["choices"][0]["message"]["content"]
        logger.info(f"Structured output: \n|{content}|")
        return content
        # TODO: Use pydantic to validate the content
        # return schema_model.model_validate(content)

    def extract_xml_tag(self, content: str, tag_name: str) -> str:
        """
        Extract text between XML tags from a string.

        Args:
            content: The string containing XML tags
            tag_name: The name of the XML tag to extract from

        Returns:
            str: The text between the opening and closing tags with strip() applied, or empty string if not found

        Examples:
            ```python
            service = OpenRouterService(
                openrouter_api_key="your-api-key",
                project_id="xml-parser"
            )
            content = "<response><answer>Paris</answer><confidence>High</confidence></response>"
            answer = service.extract_xml_tag(content, "answer")  # Returns "Paris"
            confidence = service.extract_xml_tag(content, "confidence")  # Returns "High"
            ```
        """
        # Create the pattern to match opening and closing tags
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"

        # Use re.DOTALL to make . match newlines as well
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # Return the text between the tags (group 1)
            return match.group(1).strip()
        else:
            logger.warning(f"Tag '{tag_name}' not found in content")
            return ""

    def extract_xml_boolean(self, content: str) -> bool:
        """
        Extract boolean value from standardized <boolean> XML tag.

        Expects AI responses to use 0 for False and 1 for True in <boolean> tags.
        This method provides a standardized way to handle boolean responses across all projects.

        Args:
            content: The string containing the <boolean> XML tag

        Returns:
            bool: True if the tag contains "1", False if it contains "0" or is missing

        Examples:
            ```python
            service = OpenRouterService(
                openrouter_api_key="your-api-key",
                project_id="boolean-parser"
            )

            # AI response: "<boolean>1</boolean>"
            result = service.extract_xml_boolean(response)  # Returns True

            # AI response: "<boolean>0</boolean>"
            result = service.extract_xml_boolean(response)  # Returns False

            # Missing tag or invalid content
            result = service.extract_xml_boolean(response)  # Returns False
            ```

        Note:
            Always use this method for boolean AI responses. Configure your prompts to respond with:
            "Respond with 1 if condition is true, 0 if false: <boolean>1</boolean>"
        """
        value = self.extract_xml_tag(content, "boolean")

        # Convert to boolean: "1" is True, anything else is False
        try:
            return bool(int(value)) if value.isdigit() else False
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid boolean value in <boolean> tag: '{value}', defaulting to False"
            )
            return False
