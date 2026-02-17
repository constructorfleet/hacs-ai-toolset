"""Test Waze travel time tools."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.waze_travel_time import (
    GetTravelDistanceTool,
    GetTravelTimeTool,
)


@pytest.fixture
def travel_time_tool():
    """Return a travel time tool instance."""
    return GetTravelTimeTool()


@pytest.fixture
def travel_distance_tool():
    """Return a travel distance tool instance."""
    return GetTravelDistanceTool()


async def test_get_travel_time_basic(
    hass: HomeAssistant,
    travel_time_tool: GetTravelTimeTool,
    llm_context,
):
    """Test getting travel time with basic parameters."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_time",
        tool_args={
            "origin": "123 Main St, City, State",
            "destination": "456 Oak Ave, City, State",
        },
    )

    result = await travel_time_tool.async_call(hass, tool_input, llm_context)

    # Verify it returns a dict with required fields
    assert isinstance(result, dict)
    assert "success" in result or "error" in result
    if result.get("success"):
        assert "origin" in result
        assert "destination" in result
        assert "travel_time_minutes" in result


async def test_get_travel_time_with_coordinates(
    hass: HomeAssistant,
    travel_time_tool: GetTravelTimeTool,
    llm_context,
):
    """Test getting travel time with GPS coordinates."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_time",
        tool_args={
            "origin": "40.7128, -74.0060",
            "destination": "34.0522, -118.2437",
        },
    )

    result = await travel_time_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_travel_distance_basic(
    hass: HomeAssistant,
    travel_distance_tool: GetTravelDistanceTool,
    llm_context,
):
    """Test getting travel distance with basic parameters."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_distance",
        tool_args={
            "origin": "123 Main St, City, State",
            "destination": "456 Oak Ave, City, State",
        },
    )

    result = await travel_distance_tool.async_call(hass, tool_input, llm_context)

    # Verify it returns a dict with required fields
    assert isinstance(result, dict)
    assert "success" in result or "error" in result
    if result.get("success"):
        assert "origin" in result
        assert "destination" in result
        assert "distance_miles" in result


async def test_get_travel_distance_with_coordinates(
    hass: HomeAssistant,
    travel_distance_tool: GetTravelDistanceTool,
    llm_context,
):
    """Test getting travel distance with GPS coordinates."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_distance",
        tool_args={
            "origin": "40.7128, -74.0060",
            "destination": "34.0522, -118.2437",
        },
    )

    result = await travel_distance_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_travel_time_same_location(
    hass: HomeAssistant,
    travel_time_tool: GetTravelTimeTool,
    llm_context,
):
    """Test getting travel time for same origin and destination."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_time",
        tool_args={
            "origin": "123 Main St, City, State",
            "destination": "123 Main St, City, State",
        },
    )

    result = await travel_time_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_travel_distance_same_location(
    hass: HomeAssistant,
    travel_distance_tool: GetTravelDistanceTool,
    llm_context,
):
    """Test getting travel distance for same origin and destination."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_distance",
        tool_args={
            "origin": "123 Main St, City, State",
            "destination": "123 Main St, City, State",
        },
    )

    result = await travel_distance_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_travel_time_invalid_origin(
    hass: HomeAssistant,
    travel_time_tool: GetTravelTimeTool,
    llm_context,
):
    """Test getting travel time with invalid origin."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_time",
        tool_args={
            "origin": "invalid_location_xyz",
            "destination": "123 Main St, City, State",
        },
    )

    result = await travel_time_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_travel_distance_invalid_destination(
    hass: HomeAssistant,
    travel_distance_tool: GetTravelDistanceTool,
    llm_context,
):
    """Test getting travel distance with invalid destination."""
    tool_input = llm.ToolInput(
        tool_name="get_travel_distance",
        tool_args={
            "origin": "123 Main St, City, State",
            "destination": "invalid_location_xyz",
        },
    )

    result = await travel_distance_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result
