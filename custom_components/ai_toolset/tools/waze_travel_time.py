"""Waze travel time tools for AI Toolset."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from voluptuous import Required, Schema

_LOGGER = logging.getLogger(__name__)


class GetTravelTimeTool(llm.Tool):
    """Tool for getting travel time using Waze."""

    name = "get_travel_time"
    description = (
        "Get estimated travel time between two locations using Waze navigation data. "
        "Provide origin and destination as addresses or GPS coordinates. "
        "Returns travel time in minutes based on current traffic conditions. "
        "Useful for planning trips, checking commute times, or estimating arrival times."
    )
    parameters = Schema(
        {
            Required("origin"): str,
            Required("destination"): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Get travel time from Waze."""
        origin = tool_input.tool_args["origin"]
        destination = tool_input.tool_args["destination"]

        try:
            # Call the Waze travel time service
            result = await hass.services.async_call(
                "waze_travel_time",
                "get_travel_time",
                {
                    "origin": origin,
                    "destination": destination,
                    "region": "us",
                    "units": "imperial",
                    "vehicle_type": "car",
                    "avoid_tolls": False,
                },
                blocking=True,
                return_response=True,
            )

            # Extract travel time from result
            if result and "duration" in result:
                travel_time = result["duration"]
                return {
                    "success": True,
                    "origin": origin,
                    "destination": destination,
                    "travel_time_minutes": travel_time,
                    "message": f"Travel time from '{origin}' to '{destination}' is {travel_time} minutes",
                }
            else:
                return {
                    "success": False,
                    "error": "Unable to retrieve travel time from Waze service",
                }

        except Exception as err:
            _LOGGER.exception("Error getting travel time from Waze")
            return {
                "success": False,
                "error": str(err),
            }


class GetTravelDistanceTool(llm.Tool):
    """Tool for getting travel distance using Waze."""

    name = "get_travel_distance"
    description = (
        "Get estimated travel distance between two locations using Waze navigation data. "
        "Provide origin and destination as addresses or GPS coordinates. "
        "Returns distance in miles based on recommended route. "
        "Useful for planning trips, checking route lengths, or estimating fuel needs."
    )
    parameters = Schema(
        {
            Required("origin"): str,
            Required("destination"): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Get travel distance from Waze."""
        origin = tool_input.tool_args["origin"]
        destination = tool_input.tool_args["destination"]

        try:
            # Call the Waze travel time service
            result = await hass.services.async_call(
                "waze_travel_time",
                "get_travel_time",
                {
                    "origin": origin,
                    "destination": destination,
                    "region": "us",
                    "units": "imperial",
                    "vehicle_type": "car",
                    "avoid_tolls": False,
                },
                blocking=True,
                return_response=True,
            )

            # Extract distance from result
            if result and "distance" in result:
                distance = result["distance"]
                return {
                    "success": True,
                    "origin": origin,
                    "destination": destination,
                    "distance_miles": distance,
                    "message": f"Distance from '{origin}' to '{destination}' is {distance} miles",
                }
            else:
                return {
                    "success": False,
                    "error": "Unable to retrieve travel distance from Waze service",
                }

        except Exception as err:
            _LOGGER.exception("Error getting travel distance from Waze")
            return {
                "success": False,
                "error": str(err),
            }
