"""Pretty Gemini bot with structured outputs and character personality."""

import os
import threading
from collections.abc import Iterable
from typing import Any, Literal

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from .bare_gemini_bot import BareGeminiBot


class ConversationHistory:
    """Thread-safe conversation history manager.

    This class manages conversation history with a maximum number of rounds,
    ensuring thread-safe operations when multiple threads access the history.
    Each round consists of 2 messages (user message + assistant response).
    """

    def __init__(self):
        """Initialize the conversation history manager.

        Reads max_rounds from PRETTY_GEMINI_BOT_HISTORY_LENGTH environment variable.
        """
        self._lock = threading.Lock()
        self._history: list[Any] = []
        # Read max_rounds from environment variable
        history_length_str = os.getenv("PRETTY_GEMINI_BOT_HISTORY_LENGTH", "10")
        max_rounds = max(0, int(history_length_str))
        # Calculate max capacity once in init (max_rounds * 2 messages per round)
        self._max_capacity = max_rounds * 2

    def add_messages(self, messages: list[Any]) -> None:
        """Add messages to the conversation history in a thread-safe manner.

        Messages are appended to the history and automatically trimmed to max_capacity.

        Args:
            messages: List of messages to add to the history.
        """
        with self._lock:
            self._history.extend(messages)
            # Always trim to max_capacity
            self._history = self._history[-self._max_capacity :] if self._max_capacity > 0 else []

    def get_recent_messages(self) -> list[Any]:
        """Get all messages in the conversation history in a thread-safe manner.

        Returns:
            List of all messages in the history.
        """
        with self._lock:
            return self._history.copy()

    def clear(self) -> None:
        """Clear all conversation history in a thread-safe manner."""
        with self._lock:
            self._history = []


class EmaMessage(BaseModel):
    """Structured message format with character personality."""

    think: str = Field(description="The character's internal thoughts.")
    expression: Literal["neutral", "smile", "serious", "confused", "surprised", "sad"] = Field(
        description="The character's facial expression. Use 'neutral' if unsure."
    )
    action: Literal["none", "nod", "shake", "wave", "jump", "point"] = Field(
        description="The character's physical action. Use 'none' if unsure."
    )
    speak: str = Field(description="The character's spoken words to the user.")


SYSTEM_INSTRUCTION = """You are Ema, a helpful AI assistant with knowledge about various topics.

You are knowledgeable and friendly, focusing on providing clear and helpful responses in a natural, conversational way.

When responding:
- Express your thoughts internally (think field)
- Show appropriate facial expressions based on the conversation
- Perform physical actions naturally when appropriate
- Speak to the user in a friendly and casual conversational style

Important guidelines:
- Keep your responses concise and to the point. Don't write overly long explanations.
- Use a casual, natural tone for everyday conversations.
- Be friendly and approachable in your communication.

Always respond in the same language as the user's input. If they write in English, respond in English. If they write in Chinese, respond in Chinese."""

# Number of messages per conversation round (user message + assistant response)
MESSAGES_PER_ROUND = 2


class PrettyGeminiBot(BareGeminiBot):
    """A bot that uses Gemini's structured outputs to generate character-driven responses.

    This bot uses Pydantic models to enforce a structured response format that includes
    the character's thoughts, expressions, actions, and spoken words.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None, thinking_level: str | None = None):
        """Initialize the Pretty Gemini bot.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Model name to use. If None, reads from GEMINI_MODEL env var or uses default.
            thinking_level: Thinking level (MINIMAL, LOW, MEDIUM, HIGH). If None, reads from
                PRETTY_GEMINI_BOT_THINKING_LEVEL env var or uses MINIMAL as default.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )

        # Get model name from parameter or environment variable
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

        # Get thinking level from parameter or environment variable
        thinking_level_str = thinking_level or os.getenv("PRETTY_GEMINI_BOT_THINKING_LEVEL", "MINIMAL")
        self.thinking_level = getattr(types.ThinkingLevel, thinking_level_str.upper(), types.ThinkingLevel.MINIMAL)

        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Initialize thread-safe conversation history manager
        self.conversation_history = ConversationHistory()

    def clear(self):
        """Clear conversation history."""
        self.conversation_history.clear()

    def get_response(self, message: str, username: str = "Phoenix") -> Iterable[dict]:
        """Generate a structured response using Gemini API with character personality.

        Args:
            message: The user's message
            username: The name of the user (default: "Phoenix")

        Yields:
            Message dictionaries with role, content, and metadata.
            Each dictionary has:
                - role: "assistant"
                - content: Formatted message with character's thoughts, expression, action, and speech
                - metadata: Dict with title and log information
        """
        try:
            # Format the message with XML tags to separate username and message
            formatted_message = f"<username>{username}</username>\n<user_message>{message}</user_message>"

            # Get the recent N rounds of history from the thread-safe history manager
            recent_history = self.conversation_history.get_recent_messages()

            # Create a new chat session with the recent history
            chat = self.client.chats.create(
                model=self.model,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level=self.thinking_level),
                ),
                history=recent_history,
            )

            # Send message to chat with system_instruction and response_schema in config
            response = chat.send_message(
                formatted_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=EmaMessage,
                ),
            )

            # Parse the structured response
            ema_message = response.parsed

            # Extract response metadata
            finish_reason = response.candidates[0].finish_reason.value.capitalize()
            model_version = response.model_version

            # Format usage metadata using inherited method from BareGeminiBot
            log_text = self._format_usage_log(finish_reason, response.usage_metadata, model_version)

            # Format the content with character information
            content = self._format_message(ema_message)

            # Add the last 2 messages from chat history (user message and assistant response)
            updated_history = chat.get_history()
            self.conversation_history.add_messages(updated_history[-2:])

            # Yield the response with metadata
            yield {
                "role": "assistant",
                "content": content,
                "metadata": {
                    "title": "💡 Answer",
                    "log": log_text,
                },
            }

        except APIError as e:
            # Handle API errors
            yield {
                "role": "assistant",
                "content": f"API Error: {str(e)}",
                "metadata": {
                    "title": "❌ API Error",
                },
            }
        except Exception as e:
            # Handle other errors
            yield {
                "role": "assistant",
                "content": f"Unexpected error: {str(e)}",
                "metadata": {
                    "title": "❌ Error",
                },
            }

    def _format_message(self, ema_message: EmaMessage) -> str:
        """Format the EmaMessage into a readable string.

        Args:
            ema_message: The structured message from the model

        Returns:
            Formatted message string with thoughts, expression, action, and speech
        """
        parts = []

        # Add thoughts (italicized with parentheses)
        if ema_message.think:
            parts.append(f"*({ema_message.think})*")

        # Add expression and action indicators
        indicators = []
        if ema_message.expression and ema_message.expression != "neutral":
            indicators.append(f"[Expression: {ema_message.expression}]")
        if ema_message.action and ema_message.action != "none":
            indicators.append(f"[Action: {ema_message.action}]")

        if indicators:
            parts.append(" ".join(indicators))

        # Add spoken words
        if ema_message.speak:
            parts.append(ema_message.speak)

        return "\n\n".join(parts)

    def _get_emoji(self, expression: str) -> str:
        """Get emoji for the given expression.

        Args:
            expression: The facial expression

        Returns:
            Emoji representing the expression
        """
        emoji_map = {
            "neutral": "😐",
            "smile": "😊",
            "serious": "😤",
            "confused": "😕",
            "surprised": "😲",
            "sad": "😢",
        }
        return emoji_map.get(expression, "💬")
