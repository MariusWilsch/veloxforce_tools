# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-04-30

### Added
- Renamed package from `openrouter-tools` to `veloxforce-tools`
- Added EmailService for IMAP email operations
- Added methods for fetching emails by ID
- Added methods for moving emails between folders
- Added methods for listing email folders
- Added imap-tools dependency

### Changed
- Updated package description to reflect expanded functionality
- Updated imports and documentation to use the new package name

## [0.3.1] - 2025-04-29

### Added
- Added `py.typed` marker file for better type checking support
- Enhanced type annotations throughout the codebase
- Added detailed docstrings with examples for all public methods
- Improved method signatures with more specific types
- Added explicit error types in docstrings

### Changed
- Updated method return types to be more specific
- Improved parameter type annotations
- Enhanced documentation with usage examples

## [0.3.0] - 2025-04-28

### Added
- Comprehensive integration tests for all API features
- Test for image URL processing capabilities
- Test for PDF document processing capabilities
- Support for .env file in both development and production environments
- Improved documentation for environment configuration
- Detailed testing guide with examples
- Added setup.py for pip installation compatibility

### Changed
- Updated logger.py to properly handle log level parameter
- Expanded README with detailed environment and testing sections
- Completely restructured package to follow Python packaging best practices
- Moved all code into a proper `openrouter_tools` package directory
- Updated imports to use absolute imports with the package name
- Enhanced OpenRouterService to automatically use API key from environment variables

## [0.2.0] - 2025-04-27

### Added
- Environment-based configuration using Pydantic Settings
- Dynamic retry logic based on environment (DEVELOPMENT vs PRODUCTION)
- Support for .env files for configuration

### Changed
- Retry behavior now depends on environment (no retries in DEVELOPMENT, 3 retries in PRODUCTION)
- Removed max_retries parameter from OpenRouterService constructor

## [0.1.1] - 2025-04-26

### Added
- Simple Rich-based logging system
- Basic logging configuration in `logger.py`

### Changed
- Updated service files to use the new logging system
- Improved documentation with logging examples

## [0.1.0] - 2025-04-25

### Added
- Initial release
- MessageBuilder for constructing OpenRouter API messages
- OpenRouterService for interacting with the OpenRouter API
- LangfuseService for managing prompts with Langfuse
- Support for text, image, and PDF content types
- Structured output generation with Pydantic models
