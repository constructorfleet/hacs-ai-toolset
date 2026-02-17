"""Constants for the AI Toolset integration."""

DOMAIN = "ai_toolset"

# Tool names
TOOL_WEB_SEARCH = "web_search"
TOOL_URL_FETCH = "url_fetch"
TOOL_CREATE_AUTOMATION = "create_automation"
TOOL_CODE_EXECUTOR = "code_executor"

# Configuration keys
CONF_GOOGLE_API_KEY = "google_api_key"
CONF_GOOGLE_CX = "google_cx"
CONF_KAGI_API_KEY = "kagi_api_key"
CONF_BING_API_KEY = "bing_api_key"
CONF_DEFAULT_SEARCH_ENGINE = "default_search_engine"
CONF_MAX_RESULTS = "max_results"
CONF_ENABLE_CODE_EXECUTOR = "enable_code_executor"

# Defaults
DEFAULT_MAX_RESULTS = 5
DEFAULT_SEARCH_ENGINE = "google"
DEFAULT_ENABLE_CODE_EXECUTOR = False

# Search engines
SEARCH_ENGINE_GOOGLE = "google"
SEARCH_ENGINE_KAGI = "kagi"
SEARCH_ENGINE_BING = "bing"

SEARCH_ENGINES = [
    SEARCH_ENGINE_GOOGLE,
    SEARCH_ENGINE_KAGI,
    SEARCH_ENGINE_BING,
]
