from pydantic import BaseModel
from typing import List, Union, Optional, Literal, Dict, Any

class TextContent(BaseModel):
    """Represents a text content item in a message."""
    type: Literal["text"] = "text"
    text: str

class ImageUrlContent(BaseModel):
    """Represents an image URL content item in a message."""
    type: Literal["image_url"] = "image_url"
    image_url: Dict[str, str]

class FileContent(BaseModel):
    """Represents a file content item in a message."""
    type: Literal["file"] = "file"
    file: Dict[str, str]

# Union type for all content types
ContentItem = Union[TextContent, ImageUrlContent, FileContent]

class Message(BaseModel):
    """
    Represents a message in the OpenRouter API format.
    
    The content field can be either a string (for simple text messages)
    or a list of content items (for messages with mixed content types).
    """
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[ContentItem]] = ""
