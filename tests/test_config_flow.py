"""Test the AI Toolset config flow."""

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.ai_toolset.const import (
    CONF_BING_API_KEY,
    CONF_DEFAULT_SEARCH_ENGINE,
    CONF_ENABLE_CODE_EXECUTOR,
    CONF_GOOGLE_API_KEY,
    CONF_GOOGLE_CX,
    CONF_KAGI_API_KEY,
    CONF_MAX_RESULTS,
    DEFAULT_ENABLE_CODE_EXECUTOR,
    DEFAULT_MAX_RESULTS,
    DOMAIN,
    SEARCH_ENGINE_BING,
    SEARCH_ENGINE_GOOGLE,
    SEARCH_ENGINE_KAGI,
)


async def test_user_form_google(hass: HomeAssistant) -> None:
    """Test we get the user form and can configure with Google."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    # Select Google
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_GOOGLE},
    )
    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["step_id"] == "google"

    # Configure Google
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_GOOGLE_API_KEY: "test_api_key",
            CONF_GOOGLE_CX: "test_cx",
            CONF_MAX_RESULTS: 5,
            CONF_ENABLE_CODE_EXECUTOR: False,
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result3["title"] == "AI Toolset (Google)"
    assert result3["data"] == {
        CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_GOOGLE,
        CONF_GOOGLE_API_KEY: "test_api_key",
        CONF_GOOGLE_CX: "test_cx",
        CONF_MAX_RESULTS: 5,
        CONF_ENABLE_CODE_EXECUTOR: False,
    }


async def test_user_form_kagi(hass: HomeAssistant) -> None:
    """Test we can configure with Kagi."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Select Kagi
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_KAGI},
    )
    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["step_id"] == "kagi"

    # Configure Kagi
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_KAGI_API_KEY: "test_kagi_key",
            CONF_MAX_RESULTS: 7,
            CONF_ENABLE_CODE_EXECUTOR: True,
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result3["title"] == "AI Toolset (Kagi)"
    assert result3["data"] == {
        CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_KAGI,
        CONF_KAGI_API_KEY: "test_kagi_key",
        CONF_MAX_RESULTS: 7,
        CONF_ENABLE_CODE_EXECUTOR: True,
    }


async def test_user_form_bing(hass: HomeAssistant) -> None:
    """Test we can configure with Bing."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Select Bing
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_BING},
    )
    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["step_id"] == "bing"

    # Configure Bing
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_BING_API_KEY: "test_bing_key",
            CONF_MAX_RESULTS: 3,
            CONF_ENABLE_CODE_EXECUTOR: False,
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result3["title"] == "AI Toolset (Bing)"
    assert result3["data"] == {
        CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_BING,
        CONF_BING_API_KEY: "test_bing_key",
        CONF_MAX_RESULTS: 3,
        CONF_ENABLE_CODE_EXECUTOR: False,
    }


async def test_google_missing_api_key(hass: HomeAssistant) -> None:
    """Test Google configuration with missing API key."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_GOOGLE},
    )

    # Try to configure without API key
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_GOOGLE_API_KEY: "",
            CONF_GOOGLE_CX: "test_cx",
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.FORM
    assert result3["errors"] == {"base": "missing_api_key"}


async def test_google_missing_cx(hass: HomeAssistant) -> None:
    """Test Google configuration with missing CX."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_GOOGLE},
    )

    # Try to configure without CX
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_GOOGLE_API_KEY: "test_key",
            CONF_GOOGLE_CX: "",
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.FORM
    assert result3["errors"] == {"base": "missing_cx"}


async def test_kagi_missing_api_key(hass: HomeAssistant) -> None:
    """Test Kagi configuration with missing API key."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_KAGI},
    )

    # Try to configure without API key
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_KAGI_API_KEY: "",
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.FORM
    assert result3["errors"] == {"base": "missing_api_key"}


async def test_bing_missing_api_key(hass: HomeAssistant) -> None:
    """Test Bing configuration with missing API key."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_BING},
    )

    # Try to configure without API key
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_BING_API_KEY: "",
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.FORM
    assert result3["errors"] == {"base": "missing_api_key"}


async def test_kagi_with_defaults(hass: HomeAssistant) -> None:
    """Test Kagi configuration uses defaults when not specified."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_KAGI},
    )

    # Configure with only required field
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            CONF_KAGI_API_KEY: "test_kagi_key",
        },
    )
    assert result3["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result3["data"][CONF_MAX_RESULTS] == DEFAULT_MAX_RESULTS
    assert result3["data"][CONF_ENABLE_CODE_EXECUTOR] == DEFAULT_ENABLE_CODE_EXECUTOR
