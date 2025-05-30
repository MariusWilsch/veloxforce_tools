"""Common schemas and enums for Veloxforce Tools."""

from enum import IntEnum


class AIBooleanResponse(IntEnum):
    """Standardized boolean responses for AI models.
    
    Use 0/1 in prompts instead of TRUE/FALSE to avoid string parsing issues.
    These values are inherently truthy/falsy in Python.
    
    Usage in prompts:
        "Respond with 1 if this is an invoice, 0 if not: <boolean>1</boolean>"
    
    Usage in code:
        from veloxforce_tools import OpenRouterService, AIBooleanResponse
        
        service = OpenRouterService(api_key="your-key")
        is_invoice = service.extract_xml_boolean(response)  # Returns True/False
    """
    FALSE = 0
    TRUE = 1
