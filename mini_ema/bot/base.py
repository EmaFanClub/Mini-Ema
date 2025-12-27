"""Base bot interface for Mini Ema."""

from abc import ABC, abstractmethod


class BaseBot(ABC):
    """Abstract base class for chat bots.

    This defines the interface that all bots must implement.
    Subclasses can implement different strategies for generating responses.
    """

    @abstractmethod
    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        """Generate a response to a user message.

        Args:
            message: The user's message
            history: Optional chat history for context

        Returns:
            List of message dictionaries with role, content, and optional metadata.
            Each dictionary should have:
                - role: "assistant"
                - content: The message text
                - metadata: Optional dict with title and other metadata
        """
        pass
