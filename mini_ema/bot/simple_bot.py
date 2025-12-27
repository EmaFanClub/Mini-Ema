"""Simple hardcoded bot implementation."""

from collections.abc import Iterable

from .base import BaseBot


class SimpleBot(BaseBot):
    """A simple bot with hardcoded responses.

    This is a basic implementation for demonstration purposes.
    It returns predefined messages regardless of user input.
    """

    def get_response(self, message: str) -> Iterable[dict]:
        """Get hardcoded AI response as structured messages.

        Args:
            message: User message (unused in hardcoded version)

        Yields:
            Message dictionaries with role, content, and optional metadata
        """
        # Yield two example responses with structured format
        yield {"role": "assistant", "content": "你好，我是Ema。", "metadata": {"title": "💭 Thinking: 我是Ema"}}
        yield {
            "role": "assistant",
            "content": "有什么可以帮助你的吗？",
            "metadata": {"title": "💭 Thinking: 很高兴认识你"},
        }
