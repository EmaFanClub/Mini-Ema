"""Simple hardcoded bot implementation."""

from collections.abc import Iterable

from .base import BaseBot


class SimpleBot(BaseBot):
    """A simple bot with hardcoded responses.

    This is a basic implementation for demonstration purposes.
    It returns predefined messages regardless of user input.
    """

    def clear(self):
        """Clear conversation history (no-op for SimpleBot)."""
        pass

    def get_response(self, message: str, username: str = "Phoenix") -> Iterable[dict]:
        """Get hardcoded AI response as structured messages.

        Args:
            message: User message (unused in hardcoded version)
            username: The name of the user (unused in hardcoded version)

        Yields:
            Message dictionaries with role, content, and optional metadata
        """
        # Yield two example responses with structured format including expression and action
        yield {
            "role": "assistant",
            "content": "[Expression: smile] [Action: wave]\n\n你好，我是Ema。",
            "metadata": {"title": "💡 Answer"},
        }
        yield {
            "role": "assistant",
            "content": "[Expression: neutral] [Action: none]\n\n请问有什么可以帮助你的吗？",
            "metadata": {"title": "💡 Answer"},
        }
