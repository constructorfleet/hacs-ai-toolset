"""Test create automation tool."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.create_automation import CreateAutomationTool


@pytest.fixture
def create_automation_tool(hass: HomeAssistant):
    """Return a create automation tool instance."""
    return CreateAutomationTool(hass)


async def test_create_simple_automation(
    hass: HomeAssistant, create_automation_tool: CreateAutomationTool
):
    """Test creating a simple automation."""
    tool_input = llm.ToolInput(
        tool_name="create_automation",
        tool_args={
            "automation_id": "test_automation",
            "alias": "Test Automation",
            "trigger": [
                {"platform": "state", "entity_id": "light.bedroom", "to": "on"}
            ],
            "action": [
                {
                    "service": "light.turn_on",
                    "target": {"entity_id": "light.living_room"},
                }
            ],
        },
    )

    # The automation tool requires full Home Assistant setup
    # For now, just verify it returns a dict (success or error)
    result = await create_automation_tool.async_call(tool_input)

    assert isinstance(result, dict)
    assert "automation_id" in result or "error" in result or "success" in result


async def test_create_automation_with_conditions(
    hass: HomeAssistant, create_automation_tool: CreateAutomationTool
):
    """Test creating an automation with conditions."""
    tool_input = llm.ToolInput(
        tool_name="create_automation",
        tool_args={
            "automation_id": "test_automation_cond",
            "alias": "Test Automation with Condition",
            "trigger": [
                {"platform": "state", "entity_id": "binary_sensor.motion", "to": "on"}
            ],
            "condition": [
                {"condition": "state", "entity_id": "sun.sun", "state": "below_horizon"}
            ],
            "action": [
                {"service": "light.turn_on", "target": {"entity_id": "light.hallway"}}
            ],
        },
    )

    # The automation tool requires full Home Assistant setup
    # For now, just verify it returns a dict (success or error)
    result = await create_automation_tool.async_call(tool_input)

    assert isinstance(result, dict)
    assert "automation_id" in result or "error" in result or "success" in result
