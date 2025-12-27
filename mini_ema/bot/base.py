"""Base bot interface for Mini Ema."""

from abc import ABC, abstractmethod
from collections.abc import Iterable


class BaseBot(ABC):
    """Abstract base class for chat bots.

    This defines the interface that all bots must implement.
    Subclasses can implement different strategies for generating responses.
    """

    @abstractmethod
    def clear(self):
        """Clear conversation history.

        This method should reset any conversation state maintained by the bot.
        """
        pass

    @abstractmethod
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
        pass
