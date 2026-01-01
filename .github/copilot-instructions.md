# Coding Guidelines

## Useful Resources

- Gemini Python API: .github/gemini.md

Always check the Gemini Python API if you need to invoke the Gemini LLM model.

## Mini Ema Python API

### Bot Interface

All bots must inherit from `BaseBot` and implement the `get_response` method with the following signature:

```python
def get_response(self, message: str, username: str = "Phoenix") -> Iterable[dict]:
    """Generate a response to a user message.
    
    Args:
        message: The user's message
        username: The name of the user (default: "Phoenix")
    
    Yields:
        Message dictionaries with role, content, and optional metadata.
        Each dictionary should have:
            - role: "assistant"
            - content: The message text
            - metadata: Optional dict with title and other metadata
    """
```

### Bot Metadata Structure

When implementing bots that inherit from `BaseBot`, the `get_response()` method should yield dictionaries with the following structure:

```python
{
    "role": "assistant",
    "content": "The actual response text",
    "metadata": {
        "title": "💡 Answer",  # Title shown in the chat bubble (can include emoji)
        "log": "Model: gemini-3-flash-preview | Finish: Stop | Prompt: 5 | Response: 8 | Thoughts: 13 | Total: 26"  # Plain text formatted metadata (optional)
    }
}
```

## Code Quality and Formatting

This project uses Ruff for code formatting and linting, following Google Python style standards.

### Using uv for Dependency Management

This project uses `uv` for managing dependencies and running tools.

**Documentation**: [docs.astral.sh/uv/](https://docs.astral.sh/uv/)

**Installation**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Using Make Commands

- **Check code style**: Run `make style` to check code formatting and linting
- **Auto-format code**: Run `make format` to automatically format code and fix linting issues
- **Build package**: Run `make build` to build the package
- **Run tests**: Run `make test` to run all tests
- **Help**: Run `make help` to see available make commands

All make commands use `uv` internally to run tools in an isolated environment.

### Ruff Configuration

The project is configured in `pyproject.toml` with:
- Line length: 119 characters
- Target Python version: 3.11
- Google Python style standards
- Import sorting with isort