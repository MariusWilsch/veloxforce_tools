import pytest
import asyncio
import os
import base64
from pprint import pprint
from dotenv import load_dotenv

from veloxforce_tools.services.openrouter_service import OpenRouterService
from veloxforce_tools.services.message_builder import MessageBuilder

# Load environment variables from .env file
load_dotenv()


@pytest.mark.asyncio
async def test_chat_completion_real_api():
    """
    Test that chat_completion returns a response when called with valid parameters.
    This test uses the real API client to make an actual request.

    Note: This test requires a valid OPENROUTER_API_KEY environment variable.
    """
    # Skip the test if no API key is provided
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY environment variable not set")

    # Create the service with the real API key
    service = OpenRouterService()

    # Create a simple message
    messages = await MessageBuilder.build_messages(
        prompt="What is the capital of France? Answer in one word."
    )

    print("Messages:", end="\n")
    pprint(messages)

    # Call the function with a simple model
    result = await service.chat_completion(
        messages=messages,
        model="deepseek/deepseek-chat-v3-0324:free",  # Use a simple, fast model
    )
    print("Result:", end="\n")
    pprint(result)

    # Assert we get a non-empty response
    assert result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_chat_completion_with_image_url():
    """
    Test that chat_completion works with image URLs.
    This test uses a publicly available image URL.

    Note: This test requires a valid OPENROUTER_API_KEY environment variable.
    """
    # Skip the test if no API key is provided
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY environment variable not set")

    # Create the service with the real API key
    service = OpenRouterService()

    # Use a publicly available image URL
    image_url = "https://picsum.photos/800/600"  # Random image from Lorem Picsum

    # Create a message with an image URL
    messages = await MessageBuilder.build_messages(
        prompt="Describe this image in detail.", image_urls=[image_url]
    )

    print("Messages with image URL:", end="\n")
    pprint(messages)

    # Call the function with a model that supports image input
    result = await service.chat_completion(
        messages=messages,
        model="deepseek/deepseek-chat-v3-0324:free",  # Use a model that supports image input
    )
    print("Image description result:", end="\n")
    pprint(result)

    # Assert we get a non-empty response
    assert result
    assert isinstance(result, str)
    # The response should contain some description of the image
    assert (
        len(result) > 50
    )  # Arbitrary length check to ensure we got a meaningful response


@pytest.mark.asyncio
async def test_chat_completion_with_pdf():
    """
    Test that chat_completion works with PDF files.
    This test uses a local PDF file from the assets directory.

    Note: This test requires a valid OPENROUTER_API_KEY environment variable.
    """
    # Skip the test if no API key is provided
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY environment variable not set")

    # Create the service with the real API key
    service = OpenRouterService()

    # Read and encode the PDF file
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "Dummy.pdf"
    )

    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF file not found at {pdf_path}")

    # Encode the PDF file to base64
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")

    # Create the data URL
    pdf_data_url = f"data:application/pdf;base64,{base64_pdf}"

    # Create a message with the PDF
    messages = await MessageBuilder.build_messages(
        prompt="Summarize the content of this PDF document.", pdf_data=pdf_data_url
    )

    print("Messages with PDF:", end="\n")
    pprint(messages)

    # Call the function with a model that supports PDF input
    result = await service.chat_completion(
        messages=messages,
        model="deepseek/deepseek-chat-v3-0324:free",  # Use a model that supports PDF input
    )
    print("PDF summary result:", end="\n")
    pprint(result)

    # Assert we get a non-empty response
    assert result
    assert isinstance(result, str)
    # The response should contain some description of the PDF content
    assert (
        len(result) > 50
    )  # Arbitrary length check to ensure we got a meaningful response
