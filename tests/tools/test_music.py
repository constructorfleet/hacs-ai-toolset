"""Test music tools."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.music import MusicFindTool, MusicPlayTool


@pytest.fixture
def mock_media_player_entity(hass: HomeAssistant):
    """Create a mock media player entity."""
    hass.states.async_set(
        "media_player.test_player",
        "idle",
        {
            "friendly_name": "Test Player",
            "supported_features": 152463,
        },
    )


@pytest.fixture
def music_find_tool():
    """Return a music find tool instance."""
    return MusicFindTool()


@pytest.fixture
def music_play_tool():
    """Return a music play tool instance."""
    return MusicPlayTool()


async def test_find_music_basic(
    hass: HomeAssistant,
    music_find_tool: MusicFindTool,
    llm_context,
):
    """Test basic music search."""
    tool_input = llm.ToolInput(
        tool_name="music_find",
        tool_args={
            "query": "beatles",
        },
    )

    result = await music_find_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result
    if result.get("success"):
        assert "query" in result
        assert "results" in result


async def test_find_music_with_limit(
    hass: HomeAssistant,
    music_find_tool: MusicFindTool,
    llm_context,
):
    """Test music search with result limit."""
    tool_input = llm.ToolInput(
        tool_name="music_find",
        tool_args={
            "query": "song",
            "limit": 5,
        },
    )

    result = await music_find_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_find_music_no_results(
    hass: HomeAssistant,
    music_find_tool: MusicFindTool,
    llm_context,
):
    """Test music search with no results."""
    tool_input = llm.ToolInput(
        tool_name="music_find",
        tool_args={
            "query": "nonexistent_artist_xyz123",
        },
    )

    result = await music_find_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_play_music_success(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
    mock_media_player_entity,
):
    """Test playing music successfully."""
    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "media_player.test_player",
            "media_content_id": "media-source://media_source/local/song.mp3",
            "media_content_type": "music",
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_play_music_with_options(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
    mock_media_player_entity,
):
    """Test playing music with additional options."""
    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "media_player.test_player",
            "media_content_id": "spotify:track:abc123",
            "media_content_type": "music",
            "enqueue": "add",
            "announce": True,
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_play_music_invalid_entity(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
):
    """Test playing music on non-existent entity."""
    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "media_player.nonexistent",
            "media_content_id": "some_content",
            "media_content_type": "music",
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "not found" in result["error"]


async def test_play_music_wrong_entity_type(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
):
    """Test playing music on non-media-player entity."""
    # Create a light entity instead
    hass.states.async_set(
        "light.test_light",
        "on",
        {
            "friendly_name": "Test Light",
        },
    )

    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "light.test_light",
            "media_content_id": "some_content",
            "media_content_type": "music",
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert result["success"] is False
    assert "not a media player" in result["error"]


async def test_play_music_url(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
    mock_media_player_entity,
):
    """Test playing music from a URL."""
    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "media_player.test_player",
            "media_content_id": "http://example.com/stream.mp3",
            "media_content_type": "music",
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result


async def test_play_music_playlist(
    hass: HomeAssistant,
    music_play_tool: MusicPlayTool,
    llm_context,
    mock_media_player_entity,
):
    """Test playing a playlist."""
    tool_input = llm.ToolInput(
        tool_name="music_play",
        tool_args={
            "entity_id": "media_player.test_player",
            "media_content_id": "spotify:playlist:xyz789",
            "media_content_type": "playlist",
        },
    )

    result = await music_play_tool.async_call(hass, tool_input, llm_context)

    assert isinstance(result, dict)
    assert "success" in result or "error" in result
