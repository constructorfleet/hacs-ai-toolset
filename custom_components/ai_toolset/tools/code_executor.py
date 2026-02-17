"""Code executor tool for AI Toolset."""
from __future__ import annotations

import asyncio
import logging
import sys
from io import StringIO
from typing import Any

from voluptuous import Optional, Required, Schema

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from ..const import CONF_ENABLE_CODE_EXECUTOR, DEFAULT_ENABLE_CODE_EXECUTOR

_LOGGER = logging.getLogger(__name__)


class CodeExecutorTool(llm.Tool):
    """Tool for executing Python code in a sandboxed environment."""

    name = "code_executor"
    description = (
        "Execute Python code in a sandboxed environment. "
        "Use this for calculations, data processing, or testing code snippets. "
        "Returns the output and any errors. "
        "WARNING: This tool can execute arbitrary code. Use with caution."
    )
    parameters = Schema({
        Required("code"): str,
        Optional("timeout", default=5): int,
    })

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the code executor tool."""
        self.hass = hass
        self.config = config
        self.enabled = config.get(CONF_ENABLE_CODE_EXECUTOR, DEFAULT_ENABLE_CODE_EXECUTOR)

    async def async_call(self, tool_input: llm.ToolInput) -> dict[str, Any]:
        """Execute Python code."""
        if not self.enabled:
            return {
                "error": "Code executor is disabled. Enable it in configuration."
            }

        code = tool_input.tool_args["code"]
        timeout = tool_input.tool_args.get("timeout", 5)

        try:
            # Execute code with timeout
            result = await asyncio.wait_for(
                self._execute_code(code), timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {
                "error": f"Code execution timed out after {timeout} seconds"
            }
        except Exception as err:
            _LOGGER.exception("Error executing code")
            return {"error": str(err)}

    async def _execute_code(self, code: str) -> dict[str, Any]:
        """Execute code in a restricted environment."""
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = StringIO()
        redirected_error = StringIO()

        try:
            sys.stdout = redirected_output
            sys.stderr = redirected_error

            # Create a restricted namespace
            # Only allow safe built-ins
            safe_builtins = {
                "abs": abs,
                "all": all,
                "any": any,
                "ascii": ascii,
                "bin": bin,
                "bool": bool,
                "chr": chr,
                "dict": dict,
                "divmod": divmod,
                "enumerate": enumerate,
                "filter": filter,
                "float": float,
                "format": format,
                "hex": hex,
                "int": int,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "iter": iter,
                "len": len,
                "list": list,
                "map": map,
                "max": max,
                "min": min,
                "next": next,
                "oct": oct,
                "ord": ord,
                "pow": pow,
                "print": print,
                "range": range,
                "repr": repr,
                "reversed": reversed,
                "round": round,
                "set": set,
                "slice": slice,
                "sorted": sorted,
                "str": str,
                "sum": sum,
                "tuple": tuple,
                "type": type,
                "zip": zip,
            }

            namespace = {
                "__builtins__": safe_builtins,
                "math": __import__("math"),
                "datetime": __import__("datetime"),
                "json": __import__("json"),
            }

            # Execute the code
            exec(code, namespace)

            output = redirected_output.getvalue()
            errors = redirected_error.getvalue()

            return {
                "success": True,
                "output": output,
                "errors": errors if errors else None,
            }

        except Exception as err:
            return {
                "success": False,
                "error": str(err),
                "output": redirected_output.getvalue(),
            }
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
