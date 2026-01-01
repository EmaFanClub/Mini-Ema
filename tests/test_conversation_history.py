"""Unit tests for ConversationHistory class."""

import threading
import time

from mini_ema.bot.conversation_history import ConversationHistory


def test_initialization():
    """Test basic initialization of ConversationHistory."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)
    assert len(history) == 0
    assert history.get_all_messages() == []


def test_add_messages():
    """Test adding messages to history."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)
    messages = ["user message", "assistant response"]
    history.add_messages(messages)
    assert len(history) == 2
    assert history.get_all_messages() == messages


def test_get_recent_messages_basic():
    """Test getting recent messages with basic scenarios."""
    history = ConversationHistory(max_rounds=3, messages_per_round=2)

    # Add 2 rounds (4 messages)
    history.add_messages(["user1", "assistant1"])
    history.add_messages(["user2", "assistant2"])

    # Get all messages (default to max_rounds=3)
    recent = history.get_recent_messages()
    assert recent == ["user1", "assistant1", "user2", "assistant2"]

    # Get last 1 round
    recent = history.get_recent_messages(max_rounds=1)
    assert recent == ["user2", "assistant2"]


def test_get_recent_messages_exceeds_history():
    """Test getting recent messages when requested rounds exceed actual history."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)

    # Add only 1 round (2 messages)
    history.add_messages(["user1", "assistant1"])

    # Request 5 rounds, but only 1 exists
    recent = history.get_recent_messages()
    assert recent == ["user1", "assistant1"]


def test_get_recent_messages_zero_rounds():
    """Test edge case when max_rounds is 0."""
    history = ConversationHistory(max_rounds=0, messages_per_round=2)

    # Add messages
    history.add_messages(["user1", "assistant1"])

    # Should return empty list when max_rounds is 0
    recent = history.get_recent_messages()
    assert recent == []

    # Explicitly request 0 rounds
    history2 = ConversationHistory(max_rounds=5, messages_per_round=2)
    history2.add_messages(["user1", "assistant1"])
    recent2 = history2.get_recent_messages(max_rounds=0)
    assert recent2 == []


def test_automatic_trimming():
    """Test that history automatically keeps only recent N rounds."""
    history = ConversationHistory(max_rounds=2, messages_per_round=2)

    # Add 4 rounds (8 messages)
    history.add_messages(["user1", "assistant1"])
    history.add_messages(["user2", "assistant2"])
    history.add_messages(["user3", "assistant3"])
    history.add_messages(["user4", "assistant4"])

    # get_recent_messages should return only last 2 rounds (4 messages)
    recent = history.get_recent_messages()
    assert recent == ["user3", "assistant3", "user4", "assistant4"]
    assert len(recent) == 4


def test_clear():
    """Test clearing conversation history."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)

    # Add messages
    history.add_messages(["user1", "assistant1"])
    assert len(history) == 2

    # Clear history
    history.clear()
    assert len(history) == 0
    assert history.get_all_messages() == []


def test_empty_history():
    """Test operations on empty history."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)

    assert len(history) == 0
    assert history.get_all_messages() == []
    assert history.get_recent_messages() == []

    # Clear empty history should not raise error
    history.clear()
    assert len(history) == 0


def test_thread_safety():
    """Test thread safety of ConversationHistory operations."""
    history = ConversationHistory(max_rounds=100, messages_per_round=2)
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

    # Verify total messages added (5 threads * 10 rounds * 2 messages per round)
    assert len(history) == 100


def test_different_messages_per_round():
    """Test with different messages_per_round values."""
    # Test with 3 messages per round
    history = ConversationHistory(max_rounds=2, messages_per_round=3)

    history.add_messages(["msg1", "msg2", "msg3"])
    history.add_messages(["msg4", "msg5", "msg6"])
    history.add_messages(["msg7", "msg8", "msg9"])

    # Should return last 2 rounds (6 messages)
    recent = history.get_recent_messages()
    assert recent == ["msg4", "msg5", "msg6", "msg7", "msg8", "msg9"]
    assert len(recent) == 6


def test_negative_max_rounds():
    """Test that negative max_rounds is handled correctly."""
    # Should be converted to 0
    history = ConversationHistory(max_rounds=-5, messages_per_round=2)
    history.add_messages(["user1", "assistant1"])

    # Should return empty list
    recent = history.get_recent_messages()
    assert recent == []


def test_array_slicing_edge_cases():
    """Test array slicing edge cases, especially when index is 0."""
    history = ConversationHistory(max_rounds=5, messages_per_round=2)

    # Add some messages
    history.add_messages(["user1", "assistant1"])
    history.add_messages(["user2", "assistant2"])

    # Request 0 rounds (edge case for array slicing with -0)
    recent = history.get_recent_messages(max_rounds=0)
    assert recent == []

    # Verify regular slicing still works
    recent = history.get_recent_messages(max_rounds=1)
    assert recent == ["user2", "assistant2"]

    recent = history.get_recent_messages(max_rounds=2)
    assert recent == ["user1", "assistant1", "user2", "assistant2"]


if __name__ == "__main__":
    # Run all tests
    test_initialization()
    test_add_messages()
    test_get_recent_messages_basic()
    test_get_recent_messages_exceeds_history()
    test_get_recent_messages_zero_rounds()
    test_automatic_trimming()
    test_clear()
    test_empty_history()
    test_thread_safety()
    test_different_messages_per_round()
    test_negative_max_rounds()
    test_array_slicing_edge_cases()
    print("All tests passed!")
