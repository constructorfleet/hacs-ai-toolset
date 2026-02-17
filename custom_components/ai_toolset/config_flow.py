"""Config flow for AI Toolset integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_BING_API_KEY,
    CONF_DEFAULT_SEARCH_ENGINE,
    CONF_ENABLE_CODE_EXECUTOR,
    CONF_GOOGLE_API_KEY,
    CONF_GOOGLE_CX,
    CONF_KAGI_API_KEY,
    CONF_MAX_RESULTS,
    DEFAULT_ENABLE_CODE_EXECUTOR,
    DEFAULT_MAX_RESULTS,
    DEFAULT_SEARCH_ENGINE,
    DOMAIN,
    SEARCH_ENGINE_BING,
    SEARCH_ENGINE_GOOGLE,
    SEARCH_ENGINE_KAGI,
)

_LOGGER = logging.getLogger(__name__)


class AIToolsetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AI Toolset."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._search_engine: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step - select search engine."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._search_engine = user_input[CONF_DEFAULT_SEARCH_ENGINE]

            # Move to engine-specific configuration
            if self._search_engine == SEARCH_ENGINE_GOOGLE:
                return await self.async_step_google()
            elif self._search_engine == SEARCH_ENGINE_KAGI:
                return await self.async_step_kagi()
            elif self._search_engine == SEARCH_ENGINE_BING:
                return await self.async_step_bing()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEFAULT_SEARCH_ENGINE, default=DEFAULT_SEARCH_ENGINE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=SEARCH_ENGINE_GOOGLE, label="Google"
                            ),
                            selector.SelectOptionDict(
                                value=SEARCH_ENGINE_KAGI, label="Kagi"
                            ),
                            selector.SelectOptionDict(
                                value=SEARCH_ENGINE_BING, label="Bing"
                            ),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_google(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Google-specific configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that API key and CX are provided
            if not user_input.get(CONF_GOOGLE_API_KEY):
                errors["base"] = "missing_api_key"
            elif not user_input.get(CONF_GOOGLE_CX):
                errors["base"] = "missing_cx"
            else:
                # Create the config entry
                data = {
                    CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_GOOGLE,
                    CONF_GOOGLE_API_KEY: user_input[CONF_GOOGLE_API_KEY],
                    CONF_GOOGLE_CX: user_input[CONF_GOOGLE_CX],
                    CONF_MAX_RESULTS: user_input.get(
                        CONF_MAX_RESULTS, DEFAULT_MAX_RESULTS
                    ),
                    CONF_ENABLE_CODE_EXECUTOR: user_input.get(
                        CONF_ENABLE_CODE_EXECUTOR, DEFAULT_ENABLE_CODE_EXECUTOR
                    ),
                }
                return self.async_create_entry(title="AI Toolset (Google)", data=data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GOOGLE_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(CONF_GOOGLE_CX): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_MAX_RESULTS, default=DEFAULT_MAX_RESULTS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=10, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(
                    CONF_ENABLE_CODE_EXECUTOR, default=DEFAULT_ENABLE_CODE_EXECUTOR
                ): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="google", data_schema=data_schema, errors=errors
        )

    async def async_step_kagi(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Kagi-specific configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that API key is provided
            if not user_input.get(CONF_KAGI_API_KEY):
                errors["base"] = "missing_api_key"
            else:
                # Create the config entry
                data = {
                    CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_KAGI,
                    CONF_KAGI_API_KEY: user_input[CONF_KAGI_API_KEY],
                    CONF_MAX_RESULTS: user_input.get(
                        CONF_MAX_RESULTS, DEFAULT_MAX_RESULTS
                    ),
                    CONF_ENABLE_CODE_EXECUTOR: user_input.get(
                        CONF_ENABLE_CODE_EXECUTOR, DEFAULT_ENABLE_CODE_EXECUTOR
                    ),
                }
                return self.async_create_entry(title="AI Toolset (Kagi)", data=data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_KAGI_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(
                    CONF_MAX_RESULTS, default=DEFAULT_MAX_RESULTS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=10, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(
                    CONF_ENABLE_CODE_EXECUTOR, default=DEFAULT_ENABLE_CODE_EXECUTOR
                ): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="kagi", data_schema=data_schema, errors=errors
        )

    async def async_step_bing(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Bing-specific configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that API key is provided
            if not user_input.get(CONF_BING_API_KEY):
                errors["base"] = "missing_api_key"
            else:
                # Create the config entry
                data = {
                    CONF_DEFAULT_SEARCH_ENGINE: SEARCH_ENGINE_BING,
                    CONF_BING_API_KEY: user_input[CONF_BING_API_KEY],
                    CONF_MAX_RESULTS: user_input.get(
                        CONF_MAX_RESULTS, DEFAULT_MAX_RESULTS
                    ),
                    CONF_ENABLE_CODE_EXECUTOR: user_input.get(
                        CONF_ENABLE_CODE_EXECUTOR, DEFAULT_ENABLE_CODE_EXECUTOR
                    ),
                }
                return self.async_create_entry(title="AI Toolset (Bing)", data=data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_BING_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(
                    CONF_MAX_RESULTS, default=DEFAULT_MAX_RESULTS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=10, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Optional(
                    CONF_ENABLE_CODE_EXECUTOR, default=DEFAULT_ENABLE_CODE_EXECUTOR
                ): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="bing", data_schema=data_schema, errors=errors
        )
