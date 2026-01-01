"""Unit tests for ConversationHistory class."""

import os
import threading
import time

from mini_ema.bot.pretty_gemini_bot import ConversationHistory


def test_initialization():
    """Test basic initialization of ConversationHistory."""
    # Set env var for testing
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "5"
    history = ConversationHistory()
    assert history._max_capacity == 10  # 5 rounds * 2 messages per round
    assert len(history._history) == 0
    assert history.get_recent_messages() == []


def test_add_messages():
    """Test adding messages to history."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "5"
    history = ConversationHistory()
    messages = ["user message", "assistant response"]
    history.add_messages(messages)
    assert len(history._history) == 2
    assert history.get_recent_messages() == messages


def test_get_recent_messages_basic():
    """Test getting recent messages with basic scenarios."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "3"
    history = ConversationHistory()

    # Add 2 rounds (4 messages)
    history.add_messages(["user1", "assistant1"])
    history.add_messages(["user2", "assistant2"])

    # Get all messages
    recent = history.get_recent_messages()
    assert recent == ["user1", "assistant1", "user2", "assistant2"]


def test_automatic_trimming():
    """Test that history automatically trims to max_capacity."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "2"
    history = ConversationHistory()  # max_capacity = 4

    # Add 4 rounds (8 messages)
    history.add_messages(["user1", "assistant1"])
    history.add_messages(["user2", "assistant2"])
    history.add_messages(["user3", "assistant3"])
    history.add_messages(["user4", "assistant4"])

    # Should only keep last 2 rounds (4 messages)
    recent = history.get_recent_messages()
    assert recent == ["user3", "assistant3", "user4", "assistant4"]
    assert len(recent) == 4


def test_automatic_trimming_on_add():
    """Test that history is automatically trimmed when adding messages."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "2"
    history = ConversationHistory()  # max_capacity = 4

    # Add 1 round
    history.add_messages(["user1", "assistant1"])
    assert len(history._history) == 2

    # Add 1 more round
    history.add_messages(["user2", "assistant2"])
    assert len(history._history) == 4

    # Add 1 more round - should trim the oldest round
    history.add_messages(["user3", "assistant3"])
    assert len(history._history) == 4  # Should still be 4 (not 6)
    assert history.get_recent_messages() == ["user2", "assistant2", "user3", "assistant3"]

    # Add another round - should trim again
    history.add_messages(["user4", "assistant4"])
    assert len(history._history) == 4
    assert history.get_recent_messages() == ["user3", "assistant3", "user4", "assistant4"]


def test_clear():
    """Test clearing conversation history."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "5"
    history = ConversationHistory()

    # Add messages
    history.add_messages(["user1", "assistant1"])
    assert len(history._history) == 2

    # Clear history
    history.clear()
    assert len(history._history) == 0
    assert history.get_recent_messages() == []


def test_empty_history():
    """Test operations on empty history."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "5"
    history = ConversationHistory()

    assert len(history._history) == 0
    assert history.get_recent_messages() == []

    # Clear empty history should not raise error
    history.clear()
    assert len(history._history) == 0


def test_zero_max_rounds():
    """Test when max_rounds is 0."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "0"
    history = ConversationHistory()

    # max_capacity should be 0
    assert history._max_capacity == 0

    # Add messages
    history.add_messages(["user1", "assistant1"])

    # Should return empty list
    recent = history.get_recent_messages()
    assert recent == []
    assert len(history._history) == 0


def test_thread_safety():
    """Test thread safety of ConversationHistory operations."""
    os.environ["PRETTY_GEMINI_BOT_HISTORY_LENGTH"] = "100"
    history = ConversationHistory()
    errors = []

    def add_messages_thread(thread_id, count):
        """Add messages from a thread."""
        try:
            for i in range(count):
                history.add_messages([f"user_{thread_id}_{i}", f"assistant_{thread_id}_{i}"])
        except Exception as e:
            errors.append(e)

    def read_messages_thread(count):
        """Read messages from a thread."""
        try:
            for _ in range(count):
                history.get_recent_messages()
                time.sleep(0.001)  # Small delay to interleave operations
        except Exception as e:
            errors.append(e)

    # Create multiple threads that add and read messages concurrently
    threads = []
    for i in range(5):
        t = threading.Thread(target=add_messages_thread, args=(i, 10))
        threads.append(t)
        t.start()

    for _ in range(3):
        t = threading.Thread(target=read_messages_thread, args=(20,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Check no errors occurred
    assert len(errors) == 0

    # Verify we don't have more than max_capacity messages
    assert len(history._history) <= 200  # 100 rounds * 2 messages


if __name__ == "__main__":
    # Run all tests
    test_initialization()
    test_add_messages()
    test_get_recent_messages_basic()
    test_automatic_trimming()
    test_automatic_trimming_on_add()
    test_clear()
    test_empty_history()
    test_zero_max_rounds()
    test_thread_safety()
    print("All tests passed!")
