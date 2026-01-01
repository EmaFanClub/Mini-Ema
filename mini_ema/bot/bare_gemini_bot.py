"""Gemini LLM bot implementation."""

import os
from collections.abc import Iterable

from google import genai
from google.genai import types
from google.genai.errors import APIError

from .base import BaseBot


class BareGeminiBot(BaseBot):
    """A bot that uses Google's Gemini API to generate responses.

    This bot integrates with the official Google GenAI SDK to provide
    AI-powered responses using the Gemini 3 Flash model with conversation history.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None, thinking_level: str | None = None):
        """Initialize the Gemini bot.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Model name to use. If None, reads from GEMINI_MODEL env var or uses default.
            thinking_level: Thinking level (MINIMAL, LOW, MEDIUM, HIGH). If None, reads from
                BARE_GEMINI_BOT_THINKING_LEVEL env var or uses MINIMAL as default.
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
        thinking_level_str = thinking_level or os.getenv("BARE_GEMINI_BOT_THINKING_LEVEL", "MINIMAL")
        self.thinking_level = getattr(types.ThinkingLevel, thinking_level_str.upper(), types.ThinkingLevel.MINIMAL)

        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Initialize chat session with thinking config
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=self.thinking_level)
            ),
        )

    def clear(self):
        """Clear conversation history by creating a new chat session."""
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=self.thinking_level)
            ),
        )

    def get_response(self, message: str, username: str = "Phoenix") -> Iterable[dict]:
        """Generate a response using Gemini API with conversation history.

        Args:
            message: The user's message
            username: The name of the user (unused, parameter ignored)

        Yields:
            Message dictionaries with role, content, and metadata.
            Each dictionary has:
                - role: "assistant"
                - content: The message text
                - metadata: Dict with title and log (plain text formatted usage info)
        """
        try:
            # Send message to chat and get response (username parameter is ignored)
            response = self.chat.send_message(message)

            # Extract response data using direct API access
            finish_reason = response.candidates[0].finish_reason.value.capitalize()
            text = response.text
            model_version = response.model_version

            # Format usage metadata as plain text
            log_text = self._format_usage_log(finish_reason, response.usage_metadata, model_version)

            # Yield the response with metadata
            yield {
                "role": "assistant",
                "content": text,
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

    def _format_usage_log(
        self, finish_reason: str, usage_metadata: types.GenerateContentResponseUsageMetadata, model_version: str
    ) -> str:
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
