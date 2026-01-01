"""Thread-safe conversation history management for chat bots."""

import threading
from typing import Any


class ConversationHistory:
    """Thread-safe conversation history manager.

    This class manages conversation history with a maximum number of rounds,
    ensuring thread-safe operations when multiple threads access the history.
    Each round consists of a user message and an assistant response.
    """

    def __init__(self, max_rounds: int = 10, messages_per_round: int = 2):
        """Initialize the conversation history manager.

        Args:
            max_rounds: Maximum number of conversation rounds to keep in history.
                       A round consists of messages_per_round messages (typically user + assistant).
                       Must be >= 0. If 0, no history is kept.
            messages_per_round: Number of messages per conversation round (default: 2).
        """
        self._lock = threading.Lock()
        self._history: list[Any] = []
        self._max_rounds = max(0, max_rounds)
        self._messages_per_round = max(1, messages_per_round)

    def add_messages(self, messages: list[Any]) -> None:
        """Add messages to the conversation history in a thread-safe manner.

        Args:
            messages: List of messages to add to the history.
        """
        with self._lock:
            self._history.extend(messages)

    def get_recent_messages(self, max_rounds: int | None = None) -> list[Any]:
        """Get the most recent N rounds of messages in a thread-safe manner.

        Args:
            max_rounds: Maximum number of rounds to retrieve. If None, uses the
                       instance's max_rounds setting. Must be >= 0.

        Returns:
            List of recent messages. If max_rounds is 0 or history is empty,
            returns an empty list.
        """
        with self._lock:
            # Use instance max_rounds if not specified
            rounds = self._max_rounds if max_rounds is None else max(0, max_rounds)

            # If rounds is 0, return empty list
            if rounds == 0:
                return []

            # Calculate the maximum number of messages to return
            max_messages = rounds * self._messages_per_round

            # Handle the edge case where max_messages is 0
            if max_messages == 0:
                return []

            # Return the last max_messages from history
            # Handle the case where max_messages >= len(history)
            return self._history[-max_messages:] if self._history else []

    def clear(self) -> None:
        """Clear all conversation history in a thread-safe manner."""
        with self._lock:
            self._history = []

    def get_all_messages(self) -> list[Any]:
        """Get all messages in the conversation history in a thread-safe manner.

        Returns:
            List of all messages in the history.
        """
        with self._lock:
            return self._history.copy()

    def __len__(self) -> int:
        """Get the number of messages in the conversation history.

        Returns:
            Number of messages in the history.
        """
        with self._lock:
            return len(self._history)
