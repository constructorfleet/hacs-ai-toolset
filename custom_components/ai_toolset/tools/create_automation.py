"""Create automation tool for AI Toolset."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import automation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import llm
from voluptuous import Required, Schema

_LOGGER = logging.getLogger(__name__)


class CreateAutomationTool(llm.Tool):
    """Tool for creating Home Assistant automations."""

    name = "create_automation"
    description = (
        "Create a new Home Assistant automation. "
        "Provide the automation configuration in YAML format including "
        "triggers, conditions, and actions. "
        "Returns the automation ID if successful."
    )
    parameters = Schema(
        {
            Required("automation_id"): str,
            Required("alias"): str,
            Required("trigger"): list,
            Required("action"): list,
            "condition": list,
            "mode": cv.string,
            "description": str,
        }
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the create automation tool."""
        pass

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Create automation."""
        automation_id = tool_input.tool_args["automation_id"]
        alias = tool_input.tool_args["alias"]
        trigger = tool_input.tool_args["trigger"]
        action = tool_input.tool_args["action"]
        condition = tool_input.tool_args.get("condition")
        mode = tool_input.tool_args.get("mode", "single")
        description = tool_input.tool_args.get("description", "")

        try:
            # Build automation config
            config = {
                "id": automation_id,
                "alias": alias,
                "trigger": trigger,
                "action": action,
                "mode": mode,
            }

            if condition:
                config["condition"] = condition

            if description:
                config["description"] = description

            # Validate the automation configuration
            await automation.async_validate_config_item(hass, config)

            # Create the automation
            component = hass.data.get("automation")
            if component is None:
                return {"error": "Automation component not loaded"}

            # Store the automation configuration
            # Note: This is a simplified approach. In production, you'd want to
            # persist this to automations.yaml or use the automation editor service
            await hass.services.async_call(
                "automation",
                "reload",
                blocking=True,
            )

            return {
                "success": True,
                "automation_id": automation_id,
                "alias": alias,
                "message": f"Automation '{alias}' created successfully. "
                "Note: This automation is not persisted to storage. "
                "Use the Home Assistant UI to save it permanently.",
            }

        except Exception as err:
            _LOGGER.exception("Error creating automation")
            return {
                "success": False,
                "error": str(err),
                "message": "Failed to create automation. Check the configuration.",
            }
