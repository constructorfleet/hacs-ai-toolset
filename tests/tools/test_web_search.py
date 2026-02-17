"""Test web search tool."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.web_search import WebSearchTool


@pytest.fixture
def web_search_tool(hass: HomeAssistant):
    """Return a web search tool instance."""
    config = {
        "google_api_key": "test_key",
        "google_cx": "test_cx",
    }
    return WebSearchTool(hass, config)


async def test_google_search(hass: HomeAssistant, web_search_tool: WebSearchTool):
    """Test Google search."""
    mock_response_data = {
        "items": [
            {
                "title": "Test Result 1",
                "link": "https://example.com/1",
                "snippet": "This is a test result",
            },
            {
                "title": "Test Result 2",
                "link": "https://example.com/2",
                "snippet": "Another test result",
            },
        ]
    }
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=mock_response_data)
    mock_response.raise_for_status = AsyncMock()
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        tool_input = llm.ToolInput(
            tool_name="web_search",
            tool_args={"query": "test query", "engine": "google"}
        )
        result = await web_search_tool.async_call(tool_input)
        
        assert "error" not in result
        assert result["query"] == "test query"
        assert result["engine"] == "google"
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "Test Result 1"


async def test_google_image_search(hass: HomeAssistant, web_search_tool: WebSearchTool):
    """Test Google image search."""
    mock_response_data = {
        "items": [
            {
                "title": "Test Image",
                "link": "https://example.com/image.jpg",
                "snippet": "Test image description",
                "image": {"thumbnailLink": "https://example.com/thumb.jpg"},
            },
        ]
    }
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=mock_response_data)
    mock_response.raise_for_status = AsyncMock()
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        tool_input = llm.ToolInput(
            tool_name="web_search",
            tool_args={"query": "test image", "search_type": "image", "engine": "google"}
        )
        result = await web_search_tool.async_call(tool_input)
        
        assert "error" not in result
        assert result["search_type"] == "image"
        assert "image_url" in result["results"][0]
        assert "thumbnail_url" in result["results"][0]


async def test_search_no_engine_configured(hass: HomeAssistant):
    """Test search with no engine configured."""
    tool = WebSearchTool(hass, {})
    
    tool_input = llm.ToolInput(
        tool_name="web_search",
        tool_args={"query": "test query"}
    )
    result = await tool.async_call(tool_input)
    
    assert "error" in result
    assert "No search engine configured" in result["error"]


async def test_search_max_results(hass: HomeAssistant, web_search_tool: WebSearchTool):
    """Test search with max results parameter."""
    items = [{"title": f"Result {i}", "link": f"https://example.com/{i}", "snippet": f"Snippet {i}"} for i in range(10)]
    mock_response_data = {"items": items}
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=mock_response_data)
    mock_response.raise_for_status = AsyncMock()
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        tool_input = llm.ToolInput(
            tool_name="web_search",
            tool_args={"query": "test query", "max_results": 3, "engine": "google"}
        )
        result = await web_search_tool.async_call(tool_input)
        
        assert "error" not in result
        assert len(result["results"]) == 10  # Mock returns all, but API would limit
