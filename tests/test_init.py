"""Test the AI Toolset integration."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ai_toolset import AIToolsetAPI, async_setup, async_setup_entry
from custom_components.ai_toolset.const import DOMAIN


async def test_async_setup(hass: HomeAssistant):
    """Test the setup of the integration."""
    assert await async_setup(hass, {})
    assert DOMAIN in hass.data


async def test_async_setup_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    """Test setting up the integration via config entry."""
    mock_config_entry.add_to_hass(hass)
    hass.data[DOMAIN] = {}

    with patch("custom_components.ai_toolset.llm.async_register_api"):
        assert await async_setup_entry(hass, mock_config_entry)
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_async_unload_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    """Test unloading a config entry."""
    mock_config_entry.add_to_hass(hass)
    hass.data[DOMAIN] = {mock_config_entry.entry_id: {}}

    from custom_components.ai_toolset import async_unload_entry

    assert await async_unload_entry(hass, mock_config_entry)
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


async def test_async_get_api_instance(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    """Test getting an API instance."""
    # Create the API
    api = AIToolsetAPI(hass, mock_config_entry)

    # Create an LLM context
    llm_context = llm.LLMContext(
        platform="test_platform",
        context=None,
        language="en",
        assistant=None,
        device_id=None,
    )

    # Get the API instance
    api_instance = await api.async_get_api_instance(llm_context)

    # Verify the instance is correct
    assert isinstance(api_instance, llm.APIInstance)
    assert api_instance.api == api
    assert api_instance.api.name == "AI Toolset"
    assert api_instance.llm_context == llm_context
    assert len(api_instance.tools) == 4  # web_search, url_fetch, create_automation, code_executor
