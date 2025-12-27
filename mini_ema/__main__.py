"""Main entry point for Mini Ema chatbot."""

import os

import gradio as gr

from .bot import GeminiBot, SimpleBot
from .ui import ChatUI


def main():
    """Main entry point for Mini Ema chat application."""
    # Create bot instances
    bots = {
        "Simple Bot": SimpleBot(),
    }

    # Add Gemini bot if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            bots["Gemini LLM"] = GeminiBot()
        except ValueError as e:
            print(f"Warning: Could not initialize Gemini bot: {e}")
    else:
        print("Warning: GEMINI_API_KEY not set. Gemini bot will not be available.")
        print("To use Gemini bot, copy .env.example to .env and add your API key.")

    # Create and launch the chat UI
    chat_ui = ChatUI(bots)
    chat_ui.launch(theme=gr.themes.Default())


if __name__ == "__main__":
    main()
