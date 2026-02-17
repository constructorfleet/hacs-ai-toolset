"""AI Toolset integration for Home Assistant LLM API."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .const import DOMAIN
from .tools import (
    CalendarAddEventTool,
    CalendarGetEventsTool,
    CalendarUpdateEventTool,
    CodeExecutorTool,
    CreateAutomationTool,
    MusicFindTool,
    MusicPlayTool,
    URLFetchTool,
    WebSearchTool,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the AI Toolset component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AI Toolset from a config entry."""
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register LLM tools
    api = AIToolsetAPI(hass, entry)
    llm.async_register_api(hass, api)

    _LOGGER.info("AI Toolset integration loaded with %d tools", len(api.tools))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


class AIToolsetAPI(llm.API):
    """AI Toolset LLM API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the API."""
        super().__init__(hass=hass, id=DOMAIN, name="AI Toolset")
        self.entry = entry

        # Initialize all tools
        config = entry.data
        self.tools = [
            WebSearchTool(hass, config),
            URLFetchTool(),
            CreateAutomationTool(),
            CodeExecutorTool(hass, config),
            CalendarGetEventsTool(),
            CalendarAddEventTool(),
            CalendarUpdateEventTool(),
            MusicFindTool(),
            MusicPlayTool(),
        ]

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return the API instance for this context.

        Args:
            llm_context: The LLM context containing platform, language, etc.

        Returns:
            An APIInstance with tools and configuration for this context.
        """
        # Get the tools for this API
        tools = await self.async_get_tools()

        # Create and return the API instance
        return llm.APIInstance(
            api=self,
            api_prompt="You have access to AI Toolset tools for web search, URL fetching, automation creation, code execution, calendar management, and music playback.",
            llm_context=llm_context,
            tools=tools,
        )

    async def async_get_tools(self) -> list[llm.Tool]:
        """Get list of LLM tools."""
        return self.tools
