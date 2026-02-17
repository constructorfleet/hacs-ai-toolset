"""Test configuration for AI Toolset."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ai_toolset.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "default_search_engine": "google",
            "google_api_key": "test_api_key",
            "google_cx": "test_cx",
            "max_results": 5,
            "enable_code_executor": False,
        },
        entry_id="test_entry",
        title="AI Toolset",
    )


@pytest.fixture
def mock_hass(hass):
    """Return a mock Home Assistant instance."""
    return hass
