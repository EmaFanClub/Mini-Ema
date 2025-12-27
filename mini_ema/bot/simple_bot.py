"""Simple hardcoded bot implementation."""

from mini_ema.bot.base import BaseBot


class SimpleBot(BaseBot):
    """A simple bot with hardcoded responses.

    This is a basic implementation for demonstration purposes.
    It returns predefined messages regardless of user input.
    """

    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        """Get hardcoded AI response as structured messages.

        Args:
            message: User message (unused in hardcoded version)
            history: Chat history (unused in hardcoded version)

        Returns:
            List of message dictionaries with role, content, and optional metadata
        """
        # Return two example responses with structured format
        return [
            {"role": "assistant", "content": "你好，我是Ema。", "metadata": {"title": "💭 Thinking: 我是Ema"}},
            {"role": "assistant", "content": "有什么可以帮助你的吗？", "metadata": {"title": "💭 Thinking: 很高兴认识你"}},
        ]
