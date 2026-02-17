# AI Toolset for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A HACS-installable Home Assistant custom component that provides LLM tools for enhanced AI assistant capabilities.

## Features

This integration provides the following tools for Home Assistant's LLM API:

### 🔍 Web Search Tool
- **Multiple Search Engines**: Google, Kagi, and Bing support
- **Text & Image Search**: Search for both web content and images
- **Configurable Results**: Control the number of results returned
- Get current information from the web in real-time

### 🌐 URL Fetch Tool
- **Content Extraction**: Fetch and parse web page content
- **Smart Parsing**: Extracts title, description, and clean text
- **HTML Support**: Optionally include raw HTML
- Perfect for reading articles, documentation, or any web content

### 🤖 Create Automation Tool
- **Automation Builder**: Create Home Assistant automations via LLM
- **Full YAML Support**: Define triggers, conditions, and actions
- **Validation**: Automatically validates automation configuration
- Streamline automation creation through conversation

### 💻 Code Executor Tool
- **Python Sandbox**: Execute Python code in a restricted environment
- **Safe Execution**: Limited to safe built-in functions
- **Timeout Protection**: Configurable execution timeout
- **Disabled by Default**: Enable with caution for security
- Useful for calculations, data processing, and testing

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/constructorfleet/hacs-ai-toolset`
6. Select "Integration" as the category
7. Click "Install"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page][releases]
2. Extract the `ai_toolset` folder from the zip
3. Copy the folder to your `custom_components` directory
4. Restart Home Assistant

## Configuration

This integration is configured via YAML in your `configuration.yaml`:

```yaml
ai_toolset:
  # Search engine configuration (at least one required for web search)
  google_api_key: YOUR_GOOGLE_API_KEY
  google_cx: YOUR_GOOGLE_CUSTOM_SEARCH_ID
  
  # Alternative: Kagi
  kagi_api_key: YOUR_KAGI_API_KEY
  
  # Alternative: Bing
  bing_api_key: YOUR_BING_API_KEY
  
  # Optional settings
  default_search_engine: google  # google, kagi, or bing
  max_results: 5  # Default number of search results
  
  # Code executor (disabled by default for security)
  enable_code_executor: false  # Set to true to enable (use with caution)
```

### Getting API Keys

#### Google Custom Search
1. Get a Google API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the "Custom Search API"
3. Create a Custom Search Engine at [Programmable Search Engine](https://programmablesearchengine.google.com/)
4. Get your Search Engine ID (CX)

#### Kagi
1. Sign up for [Kagi](https://kagi.com/)
2. Subscribe to a plan that includes API access
3. Generate an API key from your account settings

#### Bing
1. Sign up for [Microsoft Azure](https://azure.microsoft.com/)
2. Create a "Bing Search v7" resource
3. Get your API key from the resource's "Keys and Endpoint" page

## Usage

Once installed and configured, the tools are automatically available to Home Assistant's conversation AI. You can use them in your conversations with AI assistants like the built-in conversation integration or extended LLM integrations.

### Example Prompts

**Web Search:**
- "Search the web for the latest news about renewable energy"
- "Find images of modern kitchen designs"
- "What are the current weather conditions in Tokyo?"

**URL Fetch:**
- "Read this article for me: https://example.com/article"
- "Get the content from this documentation page"
- "Summarize this blog post: https://blog.example.com/post"

**Create Automation:**
- "Create an automation that turns on the living room lights when motion is detected"
- "Make an automation to notify me when the door opens after 10 PM"

**Code Executor** (when enabled):
- "Calculate the compound interest for $1000 at 5% for 10 years"
- "Parse this JSON data and extract the temperature values"

## Security Considerations

### Code Executor
The code executor tool is **disabled by default** for security reasons. When enabled:
- Runs in a restricted Python environment
- Only safe built-in functions are available
- File system access is blocked
- Network access is limited
- Execution timeout prevents infinite loops

**Only enable if you understand the security implications and trust the LLM you're using.**

### API Keys
- Store API keys securely
- Use Home Assistant secrets: `!secret google_api_key`
- Never commit API keys to version control
- Rotate keys periodically

## Development

### Prerequisites
- Python 3.13 or 3.14
- Home Assistant 2025.1.0 or later

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/constructorfleet/hacs-ai-toolset.git
cd hacs-ai-toolset

# Install uv
pip install uv

# Create virtual environment with Python 3.14
uv venv --python 3.14 .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements_dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/ai_toolset --cov-report=term-missing

# Run specific test file
pytest tests/test_init.py
```

### Linting

```bash
# Run ruff
ruff check custom_components/ tests/

# Run black
black custom_components/ tests/

# Run isort
isort custom_components/ tests/

# Fix issues automatically
ruff check --fix custom_components/ tests/
black custom_components/ tests/
isort custom_components/ tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Report a Bug](https://github.com/constructorfleet/hacs-ai-toolset/issues)
- [Request a Feature](https://github.com/constructorfleet/hacs-ai-toolset/issues)
- [Discussions](https://github.com/constructorfleet/hacs-ai-toolset/discussions)

## Acknowledgments

- Built for [Home Assistant](https://www.home-assistant.io/)
- Distributed via [HACS](https://hacs.xyz/)

---

**Note**: This is an independent project and is not affiliated with or endorsed by Home Assistant.

[releases-shield]: https://img.shields.io/github/release/constructorfleet/hacs-ai-toolset.svg
[releases]: https://github.com/constructorfleet/hacs-ai-toolset/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/constructorfleet/hacs-ai-toolset.svg
[commits]: https://github.com/constructorfleet/hacs-ai-toolset/commits/main
[license-shield]: https://img.shields.io/github/license/constructorfleet/hacs-ai-toolset.svg
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
