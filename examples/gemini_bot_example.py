"""Example: Integrating with Google Gemini API.

This example shows how to create a bot that uses the Gemini API
for generating responses. This requires the google-genai package
and a valid API key.

Installation:
    pip install google-genai

Usage:
    export GEMINI_API_KEY="your-api-key"
    python examples/gemini_bot_example.py
"""

from mini_ema.bot import BaseBot


class GeminiBot(BaseBot):
    """Bot implementation using Google Gemini API.

    This bot uses the Gemini API to generate intelligent responses
    based on user input and conversation history.
    """

    def __init__(self, model: str = "gemini-2.0-flash-exp", api_key: str | None = None):
        """Initialize the Gemini bot.

        Args:
            model: Gemini model to use
            api_key: Optional API key (if not set via environment variable)
        """
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package is required for GeminiBot. "
                "Install it with: pip install google-genai"
            )

        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.model = model

    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        """Generate response using Gemini API.

        Args:
            message: User message
            history: Chat history for context

        Returns:
            List of message dictionaries with role, content, and optional metadata
        """
        try:
            # Convert history to Gemini format if needed
            # For simplicity, we'll just use the current message
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
            )

            # Return the response
            return [
                {
                    "role": "assistant",
                    "content": response.text,
                }
            ]
        except Exception as e:
            # Handle errors gracefully
            return [
                {
                    "role": "assistant",
                    "content": f"抱歉，我遇到了一个错误: {str(e)}",
                }
            ]


# Example usage
if __name__ == "__main__":
    import os

    import gradio as gr

    from mini_ema.ui import ChatUI

    # Check for API key
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set.")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        print("Continuing anyway, but API calls will fail without a valid key.")

    # Create a Gemini bot instance
    bot = GeminiBot()

    # Create and launch the UI with the Gemini bot
    chat_ui = ChatUI(bot)
    chat_ui.launch(theme=gr.themes.Default())
