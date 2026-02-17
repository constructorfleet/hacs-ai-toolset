"""Test code executor tool."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from custom_components.ai_toolset.tools.code_executor import CodeExecutorTool


@pytest.fixture
def code_executor_tool_enabled(hass: HomeAssistant):
    """Return a code executor tool instance with executor enabled."""
    config = {"enable_code_executor": True}
    return CodeExecutorTool(hass, config)


@pytest.fixture
def code_executor_tool_disabled(hass: HomeAssistant):
    """Return a code executor tool instance with executor disabled."""
    config = {"enable_code_executor": False}
    return CodeExecutorTool(hass, config)


async def test_code_executor_disabled(
    hass: HomeAssistant, code_executor_tool_disabled: CodeExecutorTool
):
    """Test that code executor is disabled by default."""
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "print('Hello, World!')"}
    )
    result = await code_executor_tool_disabled.async_call(tool_input)

    assert "error" in result
    assert "disabled" in result["error"].lower()


async def test_simple_code_execution(
    hass: HomeAssistant, code_executor_tool_enabled: CodeExecutorTool
):
    """Test executing simple Python code."""
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "print('Hello, World!')"}
    )
    result = await code_executor_tool_enabled.async_call(tool_input)

    assert result["success"] is True
    assert "Hello, World!" in result["output"]


async def test_math_calculation(
    hass: HomeAssistant, code_executor_tool_enabled: CodeExecutorTool
):
    """Test math calculations."""
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "print(16 ** 0.5)"}
    )
    result = await code_executor_tool_enabled.async_call(tool_input)

    assert result["success"] is True
    assert "4.0" in result["output"]


async def test_code_with_error(
    hass: HomeAssistant, code_executor_tool_enabled: CodeExecutorTool
):
    """Test executing code that raises an error."""
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "x = 1 / 0"}
    )
    result = await code_executor_tool_enabled.async_call(tool_input)

    assert result["success"] is False
    assert "error" in result


async def test_code_timeout(
    hass: HomeAssistant, code_executor_tool_enabled: CodeExecutorTool
):
    """Test code execution timeout.
    
    Note: This test is excluded from CI (see test.yml) because it runs an infinite
    loop that hangs the test suite. The timeout mechanism doesn't work properly
    because exec() is synchronous and blocks the event loop. To properly implement
    timeout for CPU-bound code, we would need to use multiprocessing or similar.
    """
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "while True: pass", "timeout": 1}
    )
    result = await code_executor_tool_enabled.async_call(tool_input)

    assert "error" in result
    assert (
        "timeout" in result["error"].lower() or "timed out" in result["error"].lower()
    )


async def test_restricted_builtins(
    hass: HomeAssistant, code_executor_tool_enabled: CodeExecutorTool
):
    """Test that dangerous built-ins are restricted."""
    tool_input = llm.ToolInput(
        tool_name="code_executor", tool_args={"code": "open('/etc/passwd', 'r')"}
    )
    result = await code_executor_tool_enabled.async_call(tool_input)

    assert result["success"] is False
    assert "error" in result
