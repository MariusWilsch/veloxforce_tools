import os
import httpx
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_openrouter():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY environment variable not set")
        return

    print(f"Using API key: {api_key}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France? Answer in one word."
            }
        ],
        "temperature": 0.0,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )

            # Raise for HTTP errors
            response.raise_for_status()

            # Parse the response
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            # Extract the content from the response
            content = data["choices"][0]["message"]["content"]
            print(f"Content: {content}")
            return content

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
