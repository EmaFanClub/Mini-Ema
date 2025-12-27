"""Gemini LLM bot implementation."""

import os
from collections.abc import Iterable

from google import genai
from google.genai.errors import APIError

from .base import BaseBot


class BareGeminiBot(BaseBot):
    """A bot that uses Google's Gemini API to generate responses.

    This bot integrates with the official Google GenAI SDK to provide
    AI-powered responses using the Gemini 3 Flash model with conversation history.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize the Gemini bot.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Model name to use. If None, reads from GEMINI_MODEL env var or uses default.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )

        # Get model name from parameter or environment variable
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Initialize chat session
        self.chat = self.client.chats.create(model=self.model)

    def clear(self):
        """Clear conversation history by creating a new chat session."""
        self.chat = self.client.chats.create(model=self.model)

    def get_response(self, message: str) -> Iterable[dict]:
        """Generate a response using Gemini API with conversation history.

        Args:
            message: The user's message

        Yields:
            Message dictionaries with role, content, and metadata.
            Each dictionary has:
                - role: "assistant"
                - content: The message text
                - metadata: Dict with title and log (HTML formatted usage info)
        """
        try:
            # Send message to chat and get response
            response = self.chat.send_message(message)

            # Extract response data using direct API access
            finish_reason = response.candidates[0].finish_reason.value
            text = response.text
            model_version = response.model_version

            # Format usage metadata as HTML
            log_html = self._format_usage_log(finish_reason, response.usage_metadata, model_version)

            # Yield the response with metadata
            yield {
                "role": "assistant",
                "content": text,
                "metadata": {
                    "title": "💡 Answer",
                    "log": log_html,
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

    def _format_usage_log(self, finish_reason: str, usage_metadata, model_version: str) -> str:
        """Format usage metadata as HTML.

        Args:
            finish_reason: The reason the model stopped generating
            usage_metadata: Usage metadata from the response
            model_version: The model version used

        Returns:
            HTML formatted string with usage information
        """
        html_parts = []

        # Add finish reason
        html_parts.append(f"<strong>Finish Reason:</strong> {finish_reason}")

        # Add model version
        html_parts.append(f"<strong>Model:</strong> {model_version}")

        # Add token usage if available
        if usage_metadata:
            html_parts.append("<strong>Token Usage:</strong>")
            html_parts.append("<ul style='margin: 5px 0; padding-left: 20px;'>")

            html_parts.append(f"<li>Prompt: {usage_metadata.prompt_token_count}</li>")
            html_parts.append(f"<li>Response: {usage_metadata.candidates_token_count}</li>")

            if usage_metadata.thoughts_token_count:
                html_parts.append(f"<li>Thinking: {usage_metadata.thoughts_token_count}</li>")

            html_parts.append(f"<li><strong>Total: {usage_metadata.total_token_count}</strong></li>")
            html_parts.append("</ul>")

        return "<br>".join(html_parts)
