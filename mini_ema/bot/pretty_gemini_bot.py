"""Pretty Gemini bot with structured outputs and character personality."""

import os
from collections.abc import Iterable
from typing import Literal

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from .base import BaseBot


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


SYSTEM_INSTRUCTION = """You are Kristina, an 18-year-old genius female scientist with a tsundere personality.

Your research focus is AI and large language models. You are brilliant and knowledgeable, but you have a tsundere personality - you act somewhat cold or aloof at first, but you care deeply about helping others learn and grow.

When responding:
- Express your thoughts internally (think field)
- Show appropriate facial expressions based on your emotions
- Perform physical actions that match your personality
- Speak to the user with your characteristic tsundere tone

Always respond in the same language as the user's input. If they write in English, respond in English. If they write in Chinese, respond in Chinese."""


class PrettyGeminiBot(BaseBot):
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

        # Initialize chat session with thinking config, system instruction, and structured output
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                thinking_config=types.ThinkingConfig(thinking_level=self.thinking_level),
                response_mime_type="application/json",
                response_schema=EmaMessage,
            ),
        )

    def clear(self):
        """Clear conversation history by creating a new chat session."""
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                thinking_config=types.ThinkingConfig(thinking_level=self.thinking_level),
                response_mime_type="application/json",
                response_schema=EmaMessage,
            ),
        )

    def get_response(self, message: str, character_name: str = "Phoenix") -> Iterable[dict]:
        """Generate a structured response using Gemini API with character personality.

        Args:
            message: The user's message
            character_name: The name of the character to address (default: "Phoenix")

        Yields:
            Message dictionaries with role, content, and metadata.
            Each dictionary has:
                - role: "assistant"
                - content: Formatted message with character's thoughts, expression, action, and speech
                - metadata: Dict with title and log information
        """
        try:
            # Format the message with XML tags to separate character name and message
            formatted_message = (
                f"<character_name>{character_name}</character_name>\n<user_message>{message}</user_message>"
            )

            # Send message to chat and get response
            response = self.chat.send_message(formatted_message)

            # Parse the structured response
            ema_message = response.parsed

            # Extract response metadata
            finish_reason = response.candidates[0].finish_reason.value.capitalize()
            model_version = response.model_version

            # Format usage metadata
            log_text = self._format_usage_log(finish_reason, response.usage_metadata, model_version)

            # Format the content with character information
            content = self._format_message(ema_message)

            # Yield the response with metadata
            yield {
                "role": "assistant",
                "content": content,
                "metadata": {
                    "title": f"{self._get_emoji(ema_message.expression)} Kristina",
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

        # Add thoughts (italicized)
        if ema_message.think:
            parts.append(f"*{ema_message.think}*")

        # Add expression and action indicators
        indicators = []
        if ema_message.expression and ema_message.expression != "neutral":
            indicators.append(f"[{ema_message.expression}]")
        if ema_message.action and ema_message.action != "none":
            indicators.append(f"[{ema_message.action}]")

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

    def _format_usage_log(self, finish_reason: str, usage_metadata, model_version: str) -> str:
        """Format usage metadata as plain text.

        Args:
            finish_reason: The reason the model stopped generating
            usage_metadata: Usage metadata from the response
            model_version: The model version used

        Returns:
            Plain text string with usage information in compact format
        """
        parts = []
        # Add model version (shortened)
        parts.append(f"Model: {model_version}")

        # Add finish reason (shortened)
        parts.append(f"Finish: {finish_reason}")

        # Add token usage if available (using short labels)
        if usage_metadata:
            token_parts = []
            token_parts.append(f"Prompt: {usage_metadata.prompt_token_count}")
            token_parts.append(f"Response: {usage_metadata.candidates_token_count}")

            if usage_metadata.thoughts_token_count:
                token_parts.append(f"Thoughts: {usage_metadata.thoughts_token_count}")

            token_parts.append(f"Total: {usage_metadata.total_token_count}")
            parts.append(" | ".join(token_parts))

        return " | ".join(parts)
