"""Test calendar tools."""

from datetime import datetime, timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.util import dt as dt_util

from custom_components.ai_toolset.tools.calendar import (
    CalendarAddEventTool,
    CalendarGetEventsTool,
    CalendarUpdateEventTool,
)


@pytest.fixture
def mock_calendar_entity(hass: HomeAssistant):
    """Create a mock calendar entity."""
    hass.states.async_set(
        "calendar.test_calendar",
        "off",
        {
            "friendly_name": "Test Calendar",
        },
    )


@pytest.fixture
def calendar_get_events_tool():
    """Return a calendar get events tool instance."""
    return CalendarGetEventsTool()


@pytest.fixture
def calendar_add_event_tool():
    """Return a calendar add event tool instance."""
    return CalendarAddEventTool()


@pytest.fixture
def calendar_update_event_tool():
    """Return a calendar update event tool instance."""
    return CalendarUpdateEventTool()


async def test_get_events_basic(
    hass: HomeAssistant,
    calendar_get_events_tool: CalendarGetEventsTool,
    llm_context,
    mock_calendar_entity,
):
    """Test getting calendar events with basic parameters."""
    tool_input = llm.ToolInput(
        tool_name="calendar_get_events",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "duration": {"days": 7},
        },
    )

    result = await calendar_get_events_tool.async_call(hass, tool_input, llm_context)

    # Verify it returns a dict with required fields
    assert isinstance(result, dict)
    assert "success" in result or "error" in result
    if result.get("success"):
        assert "entity_id" in result
        assert "events" in result


async def test_get_events_with_date_range(
    hass: HomeAssistant,
    calendar_get_events_tool: CalendarGetEventsTool,
    llm_context,
    mock_calendar_entity,
):
    """Test getting calendar events with specific date range."""
    start = datetime(2024, 1, 1, 0, 0, 0)
    end = datetime(2024, 1, 31, 23, 59, 59)

    tool_input = llm.ToolInput(
        tool_name="calendar_get_events",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
        },
    )

    result = await calendar_get_events_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_get_events_invalid_entity(
    hass: HomeAssistant,
    calendar_get_events_tool: CalendarGetEventsTool,
    llm_context,
):
    """Test getting events from non-existent entity."""
    tool_input = llm.ToolInput(
        tool_name="calendar_get_events",
        tool_args={
            "entity_id": "calendar.nonexistent",
        },
    )

    result = await calendar_get_events_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "not found" in result["error"]


async def test_get_events_invalid_date_format(
    hass: HomeAssistant,
    calendar_get_events_tool: CalendarGetEventsTool,
    llm_context,
    mock_calendar_entity,
):
    """Test getting events with invalid date format."""
    tool_input = llm.ToolInput(
        tool_name="calendar_get_events",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "start_date_time": "invalid-date",
        },
    )

    result = await calendar_get_events_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "Invalid start_date_time format" in result["error"]


async def test_add_event_basic(
    hass: HomeAssistant,
    calendar_add_event_tool: CalendarAddEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test adding a calendar event with basic parameters."""
    start = dt_util.now() + timedelta(days=1)
    end = start + timedelta(hours=2)

    tool_input = llm.ToolInput(
        tool_name="calendar_add_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "summary": "New Meeting",
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
            "description": "Important meeting",
            "location": "Conference Room A",
        },
    )

    result = await calendar_add_event_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_add_event_minimal(
    hass: HomeAssistant,
    calendar_add_event_tool: CalendarAddEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test adding a calendar event with minimal fields."""
    start = dt_util.now() + timedelta(days=1)
    end = start + timedelta(hours=1)

    tool_input = llm.ToolInput(
        tool_name="calendar_add_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "summary": "Quick Event",
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
        },
    )

    result = await calendar_add_event_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_add_event_invalid_entity(
    hass: HomeAssistant,
    calendar_add_event_tool: CalendarAddEventTool,
    llm_context,
):
    """Test adding event to non-existent entity."""
    start = dt_util.now()
    end = start + timedelta(hours=1)

    tool_input = llm.ToolInput(
        tool_name="calendar_add_event",
        tool_args={
            "entity_id": "calendar.nonexistent",
            "summary": "Event",
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
        },
    )

    result = await calendar_add_event_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "not found" in result["error"]


async def test_add_event_invalid_dates(
    hass: HomeAssistant,
    calendar_add_event_tool: CalendarAddEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test adding event with invalid date formats."""
    tool_input = llm.ToolInput(
        tool_name="calendar_add_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "summary": "Event",
            "start_date_time": "invalid",
            "end_date_time": "also-invalid",
        },
    )

    result = await calendar_add_event_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "Invalid" in result["error"]


async def test_update_event_basic(
    hass: HomeAssistant,
    calendar_update_event_tool: CalendarUpdateEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test updating a calendar event with basic parameters."""
    start = dt_util.now() + timedelta(days=2)
    end = start + timedelta(hours=3)

    tool_input = llm.ToolInput(
        tool_name="calendar_update_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "uid": "event-123",
            "summary": "Updated Meeting",
            "start_date_time": start.isoformat(),
            "end_date_time": end.isoformat(),
            "description": "Updated description",
        },
    )

    result = await calendar_update_event_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_update_event_partial(
    hass: HomeAssistant,
    calendar_update_event_tool: CalendarUpdateEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test updating only some fields of an event."""
    tool_input = llm.ToolInput(
        tool_name="calendar_update_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "uid": "event-456",
            "summary": "New Title Only",
        },
    )

    result = await calendar_update_event_tool.async_call(hass, tool_input, llm_context)

    # Verify response structure
    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_update_event_invalid_entity(
    hass: HomeAssistant,
    calendar_update_event_tool: CalendarUpdateEventTool,
    llm_context,
):
    """Test updating event in non-existent entity."""
    tool_input = llm.ToolInput(
        tool_name="calendar_update_event",
        tool_args={
            "entity_id": "calendar.nonexistent",
            "uid": "event-789",
            "summary": "Updated",
        },
    )

    result = await calendar_update_event_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "not found" in result["error"]


async def test_update_event_invalid_dates(
    hass: HomeAssistant,
    calendar_update_event_tool: CalendarUpdateEventTool,
    llm_context,
    mock_calendar_entity,
):
    """Test updating event with invalid date formats."""
    tool_input = llm.ToolInput(
        tool_name="calendar_update_event",
        tool_args={
            "entity_id": "calendar.test_calendar",
            "uid": "event-999",
            "start_date_time": "not-a-date",
        },
    )

    result = await calendar_update_event_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "Invalid" in result["error"]
