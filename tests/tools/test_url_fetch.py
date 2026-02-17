"""Test URL fetch tool."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.url_fetch import URLFetchTool


@pytest.fixture
def url_fetch_tool(hass: HomeAssistant):
    """Return a URL fetch tool instance."""
    return URLFetchTool()


async def test_url_fetch_html_content(
    hass: HomeAssistant, url_fetch_tool: URLFetchTool, llm_context
):
    """Test fetching HTML content."""
    html_content = """
    <html>
        <head><title>Test Page</title>
        <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>Test paragraph content.</p>
        </body>
    </html>
    """

    mock_response = AsyncMock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value=html_content)
    mock_response.raise_for_status = Mock()

    with patch(
        "aiohttp.ClientSession.get",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response)),
    ):
        tool_input = llm.ToolInput(
            tool_name="url_fetch", tool_args={"url": "https://example.com"}
        )
        result = await url_fetch_tool.async_call(hass, tool_input, llm_context)

        assert "error" not in result
        assert result["url"] == "https://example.com"
        assert "Test Page" in result["title"]
        assert "Test description" in result["description"]
        assert "Test Heading" in result["text"]
        assert "Test paragraph" in result["text"]


async def test_url_fetch_non_html_content(
    hass: HomeAssistant, url_fetch_tool: URLFetchTool, llm_context
):
    """Test fetching non-HTML content."""
    text_content = "Plain text content"

    mock_response = AsyncMock()
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.text = AsyncMock(return_value=text_content)
    mock_response.raise_for_status = Mock()

    with patch(
        "aiohttp.ClientSession.get",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response)),
    ):
        tool_input = llm.ToolInput(
            tool_name="url_fetch", tool_args={"url": "https://example.com/file.txt"}
        )
        result = await url_fetch_tool.async_call(hass, tool_input, llm_context)

        assert "error" not in result
        assert result["content_type"] == "text/plain"
        assert result["text"] == text_content


async def test_url_fetch_with_max_length(
    hass: HomeAssistant, url_fetch_tool: URLFetchTool, llm_context
):
    """Test fetching content with max length limit."""
    html_content = "<html><body>" + ("x" * 20000) + "</body></html>"

    mock_response = AsyncMock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value=html_content)
    mock_response.raise_for_status = Mock()

    with patch(
        "aiohttp.ClientSession.get",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response)),
    ):
        tool_input = llm.ToolInput(
            tool_name="url_fetch",
            tool_args={"url": "https://example.com", "max_length": 100},
        )
        result = await url_fetch_tool.async_call(hass, tool_input, llm_context)

        assert "error" not in result
        assert len(result["text"]) <= 100


async def test_url_fetch_error_handling(
    hass: HomeAssistant, url_fetch_tool: URLFetchTool, llm_context
):
    """Test error handling for URL fetch."""
    with patch(
        "aiohttp.ClientSession.get", side_effect=ClientError("Connection error")
    ):
        tool_input = llm.ToolInput(
            tool_name="url_fetch", tool_args={"url": "https://example.com"}
        )
        result = await url_fetch_tool.async_call(hass, tool_input, llm_context)

        assert "error" in result
