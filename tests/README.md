# OpenRouter Tools Tests

This directory contains tests for the OpenRouter Tools package.

## Running Tests

To run the tests with Poetry:

```bash
# Install the package with development dependencies
poetry install --with dev

# Run all tests
poetry run pytest

# Run a specific test
poetry run pytest tests/test_openrouter_service.py

# Run with verbose output
poetry run pytest -v
```

If you're already in a Poetry shell (activated with `poetry shell`), you can run pytest directly:

```bash
# Run all tests
pytest

# Run a specific test
pytest tests/test_openrouter_service.py

# Run with verbose output
pytest -v
```

## Environment Variables

Some tests require environment variables to be set:

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required for tests that make real API calls)

You can set these in a `.env` file in the project root, or export them in your shell:

```bash
# Linux/macOS
export OPENROUTER_API_KEY="your-api-key"

# Windows
set OPENROUTER_API_KEY=your-api-key
```

## Test Structure

- `conftest.py`: Contains pytest fixtures and configuration
- `test_*.py`: Test files for different components

## Available Tests

### OpenRouter Service Tests

The `test_openrouter_service.py` file contains tests for the OpenRouterService class:

1. **Basic Chat Completion Test**
   - Tests the basic chat completion functionality
   - Uses a simple text prompt
   - Command: `pytest tests/test_openrouter_service.py::test_chat_completion_real_api -v -s`

2. **Image URL Test**
   - Tests the ability to process images via URLs
   - Uses a publicly available image
   - Command: `pytest tests/test_openrouter_service.py::test_chat_completion_with_image_url -v -s`

3. **PDF Processing Test**
   - Tests the ability to process PDF documents
   - Uses a local PDF file from the assets directory
   - Command: `pytest tests/test_openrouter_service.py::test_chat_completion_with_pdf -v -s`

## Troubleshooting

If you encounter issues with the tests:

1. **API Key Issues**
   - Make sure your OpenRouter API key is valid
   - Check that the environment variable is set correctly
   - Try using a different model if you're getting quota errors

2. **PDF Test Issues**
   - Ensure the PDF file exists in the assets directory
   - Check that the PDF is valid and readable
   - Try with a smaller PDF if you're getting timeout errors

3. **Image Test Issues**
   - Check that the image URL is accessible
   - Try with a different image URL if needed
   - Some models may have limitations on image processing
