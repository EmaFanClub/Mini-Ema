"""Gemini LLM bot implementation."""

import os
from collections.abc import Iterable

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

from .base import BaseBot


# Load environment variables from .env file
load_dotenv()


class GeminiBot(BaseBot):
    """A bot that uses Google's Gemini API to generate responses.

    This bot integrates with the official Google GenAI SDK to provide
    AI-powered responses using the Gemini 3 Flash model.
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

    def get_response(self, message: str) -> Iterable[dict]:
        """Generate a response using Gemini API.

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
            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
            )

            # Extract response data
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                content = candidate.content

                # Extract text from all parts
                full_text = ""
                for part in content.parts:
                    if part.text:
                        full_text += part.text

                # Get metadata
                finish_reason = candidate.finish_reason if hasattr(candidate, "finish_reason") else "UNKNOWN"
                usage_metadata = response.usage_metadata if hasattr(response, "usage_metadata") else None
                model_version = response.model_version if hasattr(response, "model_version") else self.model

                # Format usage metadata as HTML
                log_html = self._format_usage_log(finish_reason, usage_metadata, model_version)

                # Yield the response with metadata
                yield {
                    "role": "assistant",
                    "content": full_text,
                    "metadata": {
                        "title": "💡 Answer",
                        "log": log_html,
                    },
                }
            else:
                # No candidates returned
                yield {
                    "role": "assistant",
                    "content": "I apologize, but I couldn't generate a response. Please try again.",
                    "metadata": {
                        "title": "⚠️ Error",
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

            if hasattr(usage_metadata, "prompt_token_count"):
                html_parts.append(f"<li>Prompt: {usage_metadata.prompt_token_count}</li>")

            if hasattr(usage_metadata, "candidates_token_count"):
                html_parts.append(f"<li>Response: {usage_metadata.candidates_token_count}</li>")

            if hasattr(usage_metadata, "thoughts_token_count") and usage_metadata.thoughts_token_count:
                html_parts.append(f"<li>Thinking: {usage_metadata.thoughts_token_count}</li>")

            if hasattr(usage_metadata, "total_token_count"):
                html_parts.append(f"<li><strong>Total: {usage_metadata.total_token_count}</strong></li>")

            html_parts.append("</ul>")

        return "<br>".join(html_parts)
