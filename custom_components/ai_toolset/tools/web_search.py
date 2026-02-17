"""Web search tool for AI Toolset."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from voluptuous import Optional, Required, Schema

from ..const import (
    CONF_BING_API_KEY,
    CONF_GOOGLE_API_KEY,
    CONF_GOOGLE_CX,
    CONF_KAGI_API_KEY,
    DEFAULT_MAX_RESULTS,
    SEARCH_ENGINE_BING,
    SEARCH_ENGINE_GOOGLE,
    SEARCH_ENGINE_KAGI,
)

_LOGGER = logging.getLogger(__name__)


class WebSearchTool(llm.Tool):
    """Tool for performing web searches with multiple engines."""

    name = "web_search"
    description = (
        "Search the web using Google, Kagi, or Bing. "
        "Returns both text results and image results if available. "
        "Useful for finding current information, news, images, or general knowledge."
    )
    parameters = Schema(
        {
            Required("query"): str,
            Optional("search_type", default="text"): str,
            Optional("engine"): str,
            Optional("max_results", default=DEFAULT_MAX_RESULTS): int,
        }
    )

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the web search tool."""
        self.hass = hass
        self.config = config

    async def async_call(self, tool_input: llm.ToolInput) -> dict[str, Any]:
        """Execute web search."""
        query = tool_input.tool_args["query"]
        search_type = tool_input.tool_args.get("search_type", "text")
        engine = tool_input.tool_args.get("engine")
        max_results = tool_input.tool_args.get("max_results", DEFAULT_MAX_RESULTS)

        # Determine which engine to use
        if not engine:
            if CONF_GOOGLE_API_KEY in self.config:
                engine = SEARCH_ENGINE_GOOGLE
            elif CONF_KAGI_API_KEY in self.config:
                engine = SEARCH_ENGINE_KAGI
            elif CONF_BING_API_KEY in self.config:
                engine = SEARCH_ENGINE_BING
            else:
                return {"error": "No search engine configured"}

        try:
            if engine == SEARCH_ENGINE_GOOGLE:
                results = await self._search_google(query, search_type, max_results)
            elif engine == SEARCH_ENGINE_KAGI:
                results = await self._search_kagi(query, search_type, max_results)
            elif engine == SEARCH_ENGINE_BING:
                results = await self._search_bing(query, search_type, max_results)
            else:
                return {"error": f"Unknown search engine: {engine}"}

            return {
                "query": query,
                "engine": engine,
                "search_type": search_type,
                "results": results,
            }
        except Exception as err:
            _LOGGER.exception("Error performing web search")
            return {"error": str(err)}

    async def _search_google(
        self, query: str, search_type: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Search using Google Custom Search API."""
        api_key = self.config.get(CONF_GOOGLE_API_KEY)
        cx = self.config.get(CONF_GOOGLE_CX)

        if not api_key or not cx:
            raise ValueError("Google API key and CX are required")

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": min(max_results, 10),
        }

        if search_type == "image":
            params["searchType"] = "image"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                results = []
                for item in data.get("items", []):
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    if search_type == "image":
                        result["image_url"] = item.get("link", "")
                        result["thumbnail_url"] = item.get("image", {}).get(
                            "thumbnailLink", ""
                        )
                    results.append(result)

                return results

    async def _search_kagi(
        self, query: str, search_type: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Search using Kagi API."""
        api_key = self.config.get(CONF_KAGI_API_KEY)

        if not api_key:
            raise ValueError("Kagi API key is required")

        url = "https://kagi.com/api/v0/search"
        headers = {"Authorization": f"Bot {api_key}"}
        params = {"q": query, "limit": max_results}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                results = []
                for item in data.get("data", []):
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    if search_type == "image" and "thumbnail" in item:
                        result["image_url"] = item.get("url", "")
                        result["thumbnail_url"] = item.get("thumbnail", "")
                    results.append(result)

                return results

    async def _search_bing(
        self, query: str, search_type: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Search using Bing Search API."""
        api_key = self.config.get(CONF_BING_API_KEY)

        if not api_key:
            raise ValueError("Bing API key is required")

        if search_type == "image":
            url = "https://api.bing.microsoft.com/v7.0/images/search"
        else:
            url = "https://api.bing.microsoft.com/v7.0/search"

        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "count": max_results}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                results = []
                if search_type == "image":
                    for item in data.get("value", []):
                        results.append(
                            {
                                "title": item.get("name", ""),
                                "url": item.get("contentUrl", ""),
                                "image_url": item.get("contentUrl", ""),
                                "thumbnail_url": item.get("thumbnailUrl", ""),
                                "snippet": item.get("name", ""),
                            }
                        )
                else:
                    for item in data.get("webPages", {}).get("value", []):
                        results.append(
                            {
                                "title": item.get("name", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("snippet", ""),
                            }
                        )

                return results
