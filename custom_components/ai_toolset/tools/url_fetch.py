"""URL fetch tool for AI Toolset."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from voluptuous import Optional, Required, Schema

_LOGGER = logging.getLogger(__name__)


class URLFetchTool(llm.Tool):
    """Tool for fetching and parsing web page content."""

    name = "url_fetch"
    description = (
        "Fetch and extract content from a web page URL. "
        "Returns the page title, text content, and metadata. "
        "Useful for reading articles, documentation, or any web content."
    )
    parameters = Schema(
        {
            Required("url"): str,
            Optional("include_html", default=False): bool,
            Optional("max_length", default=10000): int,
        }
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the URL fetch tool."""
        self.hass = hass

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        """Fetch URL content."""
        url = tool_input.tool_args["url"]
        include_html = tool_input.tool_args.get("include_html", False)
        max_length = tool_input.tool_args.get("max_length", 10000)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; HomeAssistant/1.0)"
                    },
                ) as response:
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "")

                    if (
                        "text/html" not in content_type
                        and "application/xhtml" not in content_type
                    ):
                        # For non-HTML content, return as-is
                        text = await response.text()
                        return {
                            "url": url,
                            "content_type": content_type,
                            "text": text[:max_length],
                            "length": len(text),
                        }

                    html = await response.text()

            # Parse HTML content
            soup = BeautifulSoup(html, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            # Extract metadata
            title = ""
            if soup.title:
                title = soup.title.string or ""

            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                description = meta_desc["content"]

            result = {
                "url": url,
                "title": title,
                "description": description,
                "text": text[:max_length],
                "length": len(text),
            }

            if include_html:
                result["html"] = html[:max_length]

            return result

        except aiohttp.ClientError as err:
            _LOGGER.exception("Error fetching URL: %s", url)
            return {"error": f"Failed to fetch URL: {err}"}
        except Exception as err:
            _LOGGER.exception("Error processing URL content")
            return {"error": str(err)}
