"""Tools package for AI Toolset."""

from .calendar import (
    CalendarAddEventTool,
    CalendarGetEventsTool,
    CalendarUpdateEventTool,
)
from .code_executor import CodeExecutorTool
from .create_automation import CreateAutomationTool
from .music import MusicFindTool, MusicPlayTool
from .url_fetch import URLFetchTool
from .web_search import WebSearchTool

__all__ = [
    "WebSearchTool",
    "URLFetchTool",
    "CreateAutomationTool",
    "CodeExecutorTool",
    "CalendarGetEventsTool",
    "CalendarAddEventTool",
    "CalendarUpdateEventTool",
    "MusicFindTool",
    "MusicPlayTool",
]
