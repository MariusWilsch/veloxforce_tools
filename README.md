# Veloxforce Tools

A toolkit for working with OpenRouter, Langfuse, and Email APIs, providing easy message building, API interaction, and email management.

## Installation

```bash
# Install from local directory with pip
pip install -e /path/to/veloxforce-tools

# Or with poetry (recommended)
poetry add /path/to/veloxforce-tools

# For development
git clone https://github.com/MariusWilsch/veloxforce-tools.git
cd veloxforce-tools
poetry install  # Installs the package and all dependencies
poetry install --with dev  # Includes development dependencies
```

## Components

### EmailService

Handles email operations using IMAP:

```python
# Initialize the service
email_service = EmailService(
    imap_server="imap.example.com",
    email_address="your_email@example.com",
    password="your_password",
    folder="INBOX"  # Optional, defaults to "INBOX"
)

# Fetch emails by their IDs
emails = await email_service.fetch_emails_by_ids(["123", "456"])

# Move an email to a different folder
success = await email_service.move_email_to_folder("123", "Processed")

# List all available folders
folders = await email_service.list_folders()
```

### MessageBuilder

Helps construct properly formatted message arrays for OpenRouter API:

```python
# Build messages with text only
messages = MessageBuilder.build_messages(
    prompt="Your prompt text",
    system_prompt="Optional system instructions"
)

# Build messages with images
messages = MessageBuilder.build_messages(
    prompt="Describe this image",
    image_urls=["https://example.com/image.jpg"]
)

# Build messages with PDFs
messages = MessageBuilder.build_messages(
    prompt="Analyze this document",
    pdf_data=["data:application/pdf;base64,ABC123..."]  # Base64 encoded PDFs
)
```

### OpenRouterService

Handles communication with the OpenRouter API:

```python
# Initialize the service
openrouter_service = OpenRouterService(
    api_key="your_api_key",
    site_url="your_site_url",  # Optional
    site_name="your_site_name"  # Optional
)

# Simple chat completion
response = openrouter_service.chat_completion(
    messages=messages,
    model="anthropic/claude-3-opus"
)

# Structured output with a Pydantic model
result = openrouter_service.structured_output(
    messages=messages,
    schema_model=YourPydanticModel,
    model="anthropic/claude-3-opus"
)
```

### LangfuseService

Manages prompts and tracking with Langfuse:

```python
# Initialize the service
langfuse_service = LangfuseService(
    public_key="your_public_key",
    secret_key="your_secret_key"
)

# Get a prompt template
prompt_template = langfuse_service.get_text_prompt("prompt_name")

# Compile a prompt with variables
formatted_prompt = langfuse_service.compile_prompt(
    prompt=prompt_template,
    variables={
        "VARIABLE_1": "value_1",
        "VARIABLE_2": "value_2"
    }
)
```

## Complete Example

```python
# Initialize services
openrouter_service = OpenRouterService(api_key="your_api_key")
langfuse_service = LangfuseService(public_key="your_public_key", secret_key="your_secret_key")
email_service = EmailService(
    imap_server="imap.example.com",
    email_address="your_email@example.com",
    password="your_password"
)

# Fetch emails
emails = await email_service.fetch_emails_by_ids(["123"])
email = emails[0]

# Get and format a prompt
prompt_template = langfuse_service.get_text_prompt("document_analysis")
formatted_prompt = langfuse_service.compile_prompt(
    prompt=prompt_template,
    variables={
        "DOCUMENT_TYPE": "invoice",
        "EMAIL_SUBJECT": email.subject,
        "EMAIL_BODY": email.text
    }
)

# Build messages with PDF attachments
pdf_data = ["data:application/pdf;base64,ABC123..."]  # From email attachments
messages = MessageBuilder.build_messages(
    prompt=formatted_prompt,
    pdf_data=pdf_data
)

# Call OpenRouter
response = openrouter_service.chat_completion(
    messages=messages,
    model="anthropic/claude-3-opus"
)

# Move the processed email to a different folder
await email_service.move_email_to_folder(email.uid, "Processed")
```

## Environment Configuration

Veloxforce Tools uses Pydantic Settings for environment-based configuration:

### Setting Up Environment

Create a `.env` file in your project root:

```
# Veloxforce Tools Environment Configuration

# Environment: DEVELOPMENT or PRODUCTION
ENV=DEVELOPMENT

# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Langfuse API Keys (if using Langfuse)
# LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
# LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here

# Optional: Email Configuration (if using EmailService)
# IMAP_SERVER=imap.example.com
# EMAIL_ADDRESS=your_email@example.com
# EMAIL_PASSWORD=your_password
# EMAIL_FOLDER=INBOX

# Logging
LOG_LEVEL=INFO

# Optional: Override max retries (default is 0 for DEVELOPMENT, 3 for PRODUCTION)
# MAX_RETRIES=2
```

Or set environment variables directly:

```bash
# Linux/macOS
export ENV=PRODUCTION
export OPENROUTER_API_KEY="your-api-key"

# Windows
set ENV=PRODUCTION
set OPENROUTER_API_KEY=your-api-key
```

### Using as a Package in Other Projects

When using Veloxforce Tools as a package in other projects, you have two options:

1. **Environment Variables**: Set the required environment variables in your main project
2. **Direct Configuration**: Pass API keys directly to the service constructors

Example with direct configuration:
```python
from veloxforce_tools import OpenRouterService

# Initialize with explicit API key
service = OpenRouterService(api_key="your-api-key")
```

Example with environment variables:
```python
import os
from veloxforce_tools import OpenRouterService

# Use environment variable from parent project
service = OpenRouterService(api_key=os.environ.get("OPENROUTER_API_KEY"))
```

### Environment-Based Behavior

- **DEVELOPMENT** (default): No retries on API calls
- **PRODUCTION**: Retries API calls up to 3 times with exponential backoff

### Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| ENV | Environment (DEVELOPMENT or PRODUCTION) | DEVELOPMENT |
| OPENROUTER_API_KEY | Your OpenRouter API key | None |
| LANGFUSE_PUBLIC_KEY | Your Langfuse public key | None |
| LANGFUSE_SECRET_KEY | Your Langfuse secret key | None |
| IMAP_SERVER | IMAP server address for EmailService | None |
| EMAIL_ADDRESS | Email address for EmailService | None |
| EMAIL_PASSWORD | Email password for EmailService | None |
| EMAIL_FOLDER | Default folder for EmailService | "INBOX" |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| MAX_RETRIES | Override the default retry count | Based on ENV |

## Logging

The package includes a simple Rich-based logging system:

```python
# Import the logging configuration
from veloxforce_tools.core.logger import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Use the logger
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.warning("This is a warning message")
logger.error("This is an error message")
```

By default, the package automatically configures logging at the INFO level. You can override this by setting the `LOG_LEVEL` environment variable.

## Type Annotations and IDE Support

OpenRouter Tools includes comprehensive type annotations to improve developer experience:

- **Complete Type Hints**: All public methods and classes have detailed type annotations
- **IDE Autocompletion**: Get suggestions for methods and parameters in your IDE
- **Documentation in Code**: Rich docstrings with examples for all public methods
- **Error Types**: Explicit documentation of possible exceptions
- **py.typed Marker**: Ensures type checkers recognize the package's type annotations

Example of type annotations in action:

```python
from veloxforce_tools import OpenRouterService

# Your IDE will show parameter hints and return types
service = OpenRouterService(api_key="your-api-key")

async def example():
    # Your IDE will show parameter hints for this method
    result = await service.chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="anthropic/claude-3-haiku",
        temperature=0.7  # IDE shows this is a float parameter
    )
    # Your IDE knows this is a string
    print(result.upper())
```

Benefits:

- **Catch Errors Early**: Type checking helps identify issues before runtime
- **Better Documentation**: Types serve as documentation for expected inputs and outputs
- **Improved Refactoring**: IDEs can safely rename and refactor with type information
- **Code Navigation**: Jump to definitions and find references more easily

## Integration with Existing Project

### Installation

```bash
# Install from PyPI (once published)
# pip install veloxforce-tools

# Install from GitHub repository
pip install git+https://github.com/MariusWilsch/veloxforce-tools.git

# Or install from a local directory
pip install -e /path/to/veloxforce-tools

# With Poetry (recommended)
poetry add git+https://github.com/MariusWilsch/veloxforce-tools.git
# or from local directory
poetry add /path/to/veloxforce-tools
```

### Usage

```python
# Import the components
from veloxforce_tools import MessageBuilder, OpenRouterService, LangfuseService, EmailService

# Initialize services with explicit API keys
openrouter_service = OpenRouterService(api_key="your_api_key")
langfuse_service = LangfuseService(public_key="your_public_key", secret_key="your_secret_key")
email_service = EmailService(
    imap_server="imap.example.com",
    email_address="your_email@example.com",
    password="your_password"
)

# Or use environment variables from .env file
# Just create a .env file in your project with the necessary variables
openrouter_service = OpenRouterService()  # Will use OPENROUTER_API_KEY from .env

# Use the services as shown in the examples above
```

## Testing

The package includes tests to verify functionality. To run the tests:

```bash
# Install the package with development dependencies
poetry install --with dev

# Run the tests
poetry run pytest

# Or if you're already in a Poetry shell
pytest

# Run tests with output displayed in the console
pytest -v -s
```

### Setting Up Test Environment

Tests that make API calls require environment variables. You can set these in two ways:

1. **Using a `.env` file** (recommended for development):

   Create a `.env` file in the project root with your API keys:
   ```
   OPENROUTER_API_KEY=your-openrouter-api-key-here
   ```

2. **Setting environment variables directly**:
   ```bash
   # Linux/macOS
   export OPENROUTER_API_KEY="your-api-key"

   # Windows
   set OPENROUTER_API_KEY=your-api-key
   ```

### Test Types

The package includes several types of tests:

- **Basic functionality tests**: Test the core functionality without making API calls
- **Integration tests**: Test the integration with OpenRouter API (requires API key)
- **Image tests**: Test the image processing capabilities (requires API key)
- **PDF tests**: Test the PDF processing capabilities (requires API key)

To run specific tests:

```bash
# Run only the basic chat completion test
pytest tests/test_openrouter_service.py::test_chat_completion_real_api -v -s

# Run only the image test
pytest tests/test_openrouter_service.py::test_chat_completion_with_image_url -v -s

# Run only the PDF test
pytest tests/test_openrouter_service.py::test_chat_completion_with_pdf -v -s
```

See the [tests README](tests/README.md) for more details.

## Versioning Guidelines

This package follows [Semantic Versioning](https://semver.org/):

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
  - Changing method signatures
  - Removing public methods
  - Changing return types
  - Renaming classes or modules

- **MINOR**: Backwards-compatible functionality additions
  - Adding new methods
  - Adding optional parameters
  - Adding new classes
  - Extending functionality

- **PATCH**: Backwards-compatible bug fixes
  - Fixing bugs
  - Performance improvements
  - Documentation updates
  - Minor code refactoring

### When to Update Versions

1. **MAJOR (1.0.0 → 2.0.0)**
   - When you change the `build_messages` parameter order
   - When you remove a method from OpenRouterService
   - When you change how messages are structured

2. **MINOR (1.0.0 → 1.1.0)**
   - When you add a new method to MessageBuilder
   - When you add support for a new content type
   - When you add optional parameters

3. **PATCH (1.0.0 → 1.0.1)**
   - When you fix a bug in PDF encoding
   - When you improve error handling
   - When you optimize performance

### Version Update Process

1. Update version in `openrouter_tools/__init__.py`
2. Update CHANGELOG.md with changes
3. Commit changes with message "Bump version to X.Y.Z"
4. Tag the commit with "vX.Y.Z"
5. Push changes and tags
