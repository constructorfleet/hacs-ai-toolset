# Agent Instructions for hacs-ai-toolset

## Python Environment Setup

This project **requires Python 3.14**. All agents working on this project MUST follow these setup steps:

### 1. Install uv Package Manager
```bash
pip install uv
```

### 2. Install Python 3.14
```bash
uv python install 3.14
```

### 3. Create Virtual Environment
```bash
uv venv --python 3.14 .venv
```

### 4. Install Dependencies
Use `uv pip install` for all dependency installations:
```bash
# Install test dependencies
uv pip install -r requirements_test.txt

# Install additional packages
uv pip install <package-name>
```

## Development Workflow

### Running Tools
All development tools MUST be run via `uv run`:

```bash
# Linting with ruff
uv run ruff check .
uv run ruff check --fix .

# Formatting with black
uv run black .

# Running tests
uv run pytest
uv run pytest tests/tools/test_calendar.py -v
```

### Code Quality Requirements

Before considering any work complete, agents MUST:

1. **Write Tests**: All new functionality must have corresponding tests
2. **Run Ruff**: Fix all linting errors and warnings
   ```bash
   uv run ruff check . --fix
   ```
3. **Run Black**: Format all code
   ```bash
   uv run black .
   ```
4. **Run Tests**: Ensure all tests pass
   ```bash
   PYTHONPATH=. uv run pytest
   ```
5. **Fix All Issues**: Address all errors, warnings, and test failures

### Test Execution
When running pytest, ensure PYTHONPATH is set:
```bash
PYTHONPATH=. uv run pytest
```

## Project Structure

### Adding New Tools
When adding new LLM tools to this integration:

1. Create tool file in `custom_components/ai_toolset/tools/`
2. Implement the tool class inheriting from `llm.Tool`
3. Add tool to `custom_components/ai_toolset/tools/__init__.py`
4. Register tool in `custom_components/ai_toolset/__init__.py`
5. Create comprehensive tests in `tests/tools/`
6. Run ruff, black, and pytest to validate

### Tool Implementation Pattern
```python
from homeassistant.helpers import llm
from voluptuous import Required, Optional, Schema

class MyTool(llm.Tool):
    name = "my_tool"
    description = "Description for LLM"
    parameters = Schema({
        Required("param1"): str,
        Optional("param2"): int,
    })
    
    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict[str, Any]:
        # Implementation
        pass
```

## Testing Requirements

All tests must:
- Use pytest fixtures from `tests/conftest.py`
- Mock external services appropriately
- Test both success and failure cases
- Validate error handling
- Follow existing test patterns in the repository

## Important Notes

- **Never skip the quality checks**: Ruff, Black, and pytest must all pass
- **Python 3.14 is mandatory**: Do not use older Python versions
- **Use uv for everything**: All pip operations and tool runs must use uv
- **Write comprehensive tests**: New code without tests is incomplete
- **Follow existing patterns**: Consistency with the existing codebase is crucial
