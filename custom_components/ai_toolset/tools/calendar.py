"""Calendar tools for AI Toolset."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.util import dt as dt_util
from voluptuous import Optional, Required, Schema

_LOGGER = logging.getLogger(__name__)


class CalendarGetEventsTool(llm.Tool):
    """Tool for retrieving calendar events."""

    name = "calendar_get_events"
    description = (
        "Get events from a Home Assistant calendar. "
        "Returns upcoming events for the specified calendar entity. "
        "You can specify a start and end date/time, or get events for a duration. "
        "Useful for checking upcoming appointments, reminders, or scheduled events."
    )
    parameters = Schema(
        {
            Required("entity_id"): str,
            Optional("start_date_time"): str,
            Optional("end_date_time"): str,
            Optional("duration"): dict,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Get calendar events."""
        entity_id = tool_input.tool_args["entity_id"]
        start_date_time = tool_input.tool_args.get("start_date_time")
        end_date_time = tool_input.tool_args.get("end_date_time")
        duration = tool_input.tool_args.get("duration")

        try:
            # Validate entity exists
            state = hass.states.get(entity_id)
            if state is None:
                return {
                    "success": False,
                    "error": f"Calendar entity '{entity_id}' not found",
                }

            # Determine start and end times
            if start_date_time:
                start = dt_util.parse_datetime(start_date_time)
                if start is None:
                    return {
                        "success": False,
                        "error": f"Invalid start_date_time format: {start_date_time}",
                    }
            else:
                start = dt_util.now()

            if end_date_time:
                end = dt_util.parse_datetime(end_date_time)
                if end is None:
                    return {
                        "success": False,
                        "error": f"Invalid end_date_time format: {end_date_time}",
                    }
            elif duration:
                # Parse duration dict (e.g., {"hours": 24, "days": 7})
                try:
                    end = start + timedelta(**duration)
                except (TypeError, ValueError) as err:
                    return {
                        "success": False,
                        "error": f"Invalid duration format: {err}",
                    }
            else:
                # Default to 7 days
                end = start + timedelta(days=7)

            # Get events using the calendar service
            events = await hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": entity_id,
                    "start_date_time": start.isoformat(),
                    "end_date_time": end.isoformat(),
                },
                blocking=True,
                return_response=True,
            )

            # Format the response
            calendar_events = events.get(entity_id, {}).get("events", [])

            return {
                "success": True,
                "entity_id": entity_id,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "event_count": len(calendar_events),
                "events": calendar_events,
            }

        except Exception as err:
            _LOGGER.exception("Error retrieving calendar events")
            return {"success": False, "error": str(err)}


class CalendarAddEventTool(llm.Tool):
    """Tool for adding calendar events."""

    name = "calendar_add_event"
    description = (
        "Add a new event to a Home Assistant calendar. "
        "Creates a calendar event with title, start time, end time, and optional description. "
        "Useful for scheduling appointments, setting reminders, or creating events."
    )
    parameters = Schema(
        {
            Required("entity_id"): str,
            Required("summary"): str,
            Required("start_date_time"): str,
            Required("end_date_time"): str,
            Optional("description"): str,
            Optional("location"): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Add calendar event."""
        entity_id = tool_input.tool_args["entity_id"]
        summary = tool_input.tool_args["summary"]
        start_date_time = tool_input.tool_args["start_date_time"]
        end_date_time = tool_input.tool_args["end_date_time"]
        description = tool_input.tool_args.get("description", "")
        location = tool_input.tool_args.get("location", "")

        try:
            # Validate entity exists
            state = hass.states.get(entity_id)
            if state is None:
                return {
                    "success": False,
                    "error": f"Calendar entity '{entity_id}' not found",
                }

            # Validate date/time formats
            start = dt_util.parse_datetime(start_date_time)
            if start is None:
                return {
                    "success": False,
                    "error": f"Invalid start_date_time format: {start_date_time}",
                }

            end = dt_util.parse_datetime(end_date_time)
            if end is None:
                return {
                    "success": False,
                    "error": f"Invalid end_date_time format: {end_date_time}",
                }

            # Build service data
            service_data = {
                "entity_id": entity_id,
                "summary": summary,
                "start_date_time": start_date_time,
                "end_date_time": end_date_time,
            }

            if description:
                service_data["description"] = description

            if location:
                service_data["location"] = location

            # Create the event
            await hass.services.async_call(
                "calendar",
                "create_event",
                service_data,
                blocking=True,
            )

            return {
                "success": True,
                "entity_id": entity_id,
                "summary": summary,
                "start": start_date_time,
                "end": end_date_time,
                "message": f"Event '{summary}' created successfully",
            }

        except Exception as err:
            _LOGGER.exception("Error creating calendar event")
            return {"success": False, "error": str(err)}


class CalendarUpdateEventTool(llm.Tool):
    """Tool for updating calendar events."""

    name = "calendar_update_event"
    description = (
        "Update an existing event in a Home Assistant calendar. "
        "Modify the title, start time, end time, description, or location of a calendar event. "
        "You must provide the event UID to identify which event to update."
    )
    parameters = Schema(
        {
            Required("entity_id"): str,
            Required("uid"): str,
            Optional("summary"): str,
            Optional("start_date_time"): str,
            Optional("end_date_time"): str,
            Optional("description"): str,
            Optional("location"): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Update calendar event."""
        entity_id = tool_input.tool_args["entity_id"]
        uid = tool_input.tool_args["uid"]
        summary = tool_input.tool_args.get("summary")
        start_date_time = tool_input.tool_args.get("start_date_time")
        end_date_time = tool_input.tool_args.get("end_date_time")
        description = tool_input.tool_args.get("description")
        location = tool_input.tool_args.get("location")

        try:
            # Validate entity exists
            state = hass.states.get(entity_id)
            if state is None:
                return {
                    "success": False,
                    "error": f"Calendar entity '{entity_id}' not found",
                }

            # Build service data with only provided fields
            service_data = {
                "entity_id": entity_id,
                "uid": uid,
            }

            if summary is not None:
                service_data["summary"] = summary

            if start_date_time is not None:
                # Validate date/time format
                start = dt_util.parse_datetime(start_date_time)
                if start is None:
                    return {
                        "success": False,
                        "error": f"Invalid start_date_time format: {start_date_time}",
                    }
                service_data["start_date_time"] = start_date_time

            if end_date_time is not None:
                # Validate date/time format
                end = dt_util.parse_datetime(end_date_time)
                if end is None:
                    return {
                        "success": False,
                        "error": f"Invalid end_date_time format: {end_date_time}",
                    }
                service_data["end_date_time"] = end_date_time

            if description is not None:
                service_data["description"] = description

            if location is not None:
                service_data["location"] = location

            # Update the event
            await hass.services.async_call(
                "calendar",
                "update_event",
                service_data,
                blocking=True,
            )

            return {
                "success": True,
                "entity_id": entity_id,
                "uid": uid,
                "message": f"Event '{uid}' updated successfully",
            }

        except Exception as err:
            _LOGGER.exception("Error updating calendar event")
            return {"success": False, "error": str(err)}
