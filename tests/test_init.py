"""Test the AI Toolset integration."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ai_toolset import async_setup, async_setup_entry
from custom_components.ai_toolset.const import DOMAIN


async def test_async_setup(hass: HomeAssistant):
    """Test the setup of the integration."""
    assert await async_setup(hass, {})
    assert DOMAIN in hass.data


async def test_async_setup_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry):
    """Test setting up the integration via config entry."""
    mock_config_entry.add_to_hass(hass)
    
    with patch("custom_components.ai_toolset.llm.async_register_api"):
        assert await async_setup_entry(hass, mock_config_entry)
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry):
    """Test unloading a config entry."""
    mock_config_entry.add_to_hass(hass)
    hass.data[DOMAIN] = {mock_config_entry.entry_id: {}}
    
    from custom_components.ai_toolset import async_unload_entry
    
    assert await async_unload_entry(hass, mock_config_entry)
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]
