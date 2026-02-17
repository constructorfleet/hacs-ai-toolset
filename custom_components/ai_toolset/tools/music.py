"""Music tools for AI Toolset."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from voluptuous import Optional, Required, Schema

_LOGGER = logging.getLogger(__name__)


class MusicFindTool(llm.Tool):
    """Tool for finding music in the media library."""

    name = "music_find"
    description = (
        "Search for music in the Home Assistant media library. "
        "Search by artist, album, track name, or genre. "
        "Returns a list of matching media items that can be played. "
        "Works with Music Assistant, local media, and other media sources."
    )
    parameters = Schema(
        {
            Required("query"): str,
            Optional("media_content_type"): str,
            Optional("limit", default=10): int,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Search for music."""
        query = tool_input.tool_args["query"]
        limit = tool_input.tool_args.get("limit", 10)

        try:
            # Try to browse media sources to find matches
            # First, get available media sources
            media_sources = []

            # Check if media_source component is loaded
            if "media_source" in hass.config.components:
                try:
                    # Browse the media source root
                    browse_media = await hass.services.async_call(
                        "media_player",
                        "browse_media",
                        {
                            "media_content_type": "music",
                            "media_content_id": "media-source://media_source",
                        },
                        blocking=True,
                        return_response=True,
                    )

                    if browse_media:
                        media_sources.append(browse_media)
                except Exception as err:
                    _LOGGER.debug("Could not browse media_source: %s", err)

            # Search through Music Assistant if available
            music_assistant_entities = [
                entity_id
                for entity_id in hass.states.async_entity_ids("media_player")
                if "music_assistant" in entity_id.lower() or "mass" in entity_id.lower()
            ]

            results = []
            query_lower = query.lower()

            # Search in media sources
            for source in media_sources:
                if isinstance(source, dict):
                    items = self._search_media_items(source, query_lower, limit)
                    results.extend(items)

            # If we have Music Assistant, try to search there
            if music_assistant_entities and len(results) < limit:
                try:
                    # Try to use Music Assistant's search if available
                    ma_entity = music_assistant_entities[0]

                    # Use the media search functionality
                    await hass.services.async_call(
                        "media_player",
                        "play_media",
                        {
                            "entity_id": ma_entity,
                            "media_content_id": f"search:{query}",
                            "media_content_type": "music",
                        },
                        blocking=False,
                        return_response=False,
                    )
                except Exception as err:
                    _LOGGER.debug("Could not search Music Assistant: %s", err)

            # Limit results
            results = results[:limit]

            return {
                "success": True,
                "query": query,
                "result_count": len(results),
                "results": results,
                "message": (
                    f"Found {len(results)} results for '{query}'"
                    if results
                    else f"No results found for '{query}'"
                ),
            }

        except Exception as err:
            _LOGGER.exception("Error searching for music")
            return {"success": False, "error": str(err)}

    def _search_media_items(
        self, media_item: dict, query: str, limit: int
    ) -> list[dict[str, Any]]:
        """Recursively search media items for matches."""
        results = []

        # Check if current item matches
        title = media_item.get("title", "").lower()
        if query in title:
            results.append(
                {
                    "title": media_item.get("title"),
                    "media_content_type": media_item.get("media_content_type"),
                    "media_content_id": media_item.get("media_content_id"),
                    "thumbnail": media_item.get("thumbnail"),
                    "can_play": media_item.get("can_play", False),
                }
            )

        # Search children if available and we haven't hit the limit
        if len(results) < limit and "children" in media_item:
            for child in media_item.get("children", []):
                if len(results) >= limit:
                    break
                child_results = self._search_media_items(child, query, limit)
                results.extend(child_results)

        return results[:limit]


class MusicPlayTool(llm.Tool):
    """Tool for playing music on a media player."""

    name = "music_play"
    description = (
        "Play music on a specific Home Assistant media player. "
        "Provide the media player entity ID and the media content to play. "
        "You can use media_content_id from music_find results, or provide a URL, "
        "Music Assistant URI, or other media identifier. "
        "Optionally specify the media content type (music, playlist, album, etc.)."
    )
    parameters = Schema(
        {
            Required("entity_id"): str,
            Required("media_content_id"): str,
            Optional("media_content_type", default="music"): str,
            Optional("enqueue"): str,
            Optional("announce"): bool,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Play music on media player."""
        entity_id = tool_input.tool_args["entity_id"]
        media_content_id = tool_input.tool_args["media_content_id"]
        media_content_type = tool_input.tool_args.get("media_content_type", "music")
        enqueue = tool_input.tool_args.get("enqueue")
        announce = tool_input.tool_args.get("announce", False)

        try:
            # Validate entity exists
            state = hass.states.get(entity_id)
            if state is None:
                return {
                    "success": False,
                    "error": f"Media player entity '{entity_id}' not found",
                }

            # Validate it's a media player entity
            if not entity_id.startswith("media_player."):
                return {
                    "success": False,
                    "error": f"Entity '{entity_id}' is not a media player",
                }

            # Build service data
            service_data = {
                "entity_id": entity_id,
                "media_content_id": media_content_id,
                "media_content_type": media_content_type,
            }

            if enqueue:
                service_data["enqueue"] = enqueue

            if announce:
                service_data["announce"] = announce

            # Play the media
            await hass.services.async_call(
                "media_player",
                "play_media",
                service_data,
                blocking=True,
            )

            return {
                "success": True,
                "entity_id": entity_id,
                "media_content_id": media_content_id,
                "media_content_type": media_content_type,
                "message": f"Playing media on '{entity_id}'",
            }

        except Exception as err:
            _LOGGER.exception("Error playing music")
            return {"success": False, "error": str(err)}
