"""Main entry point for Mini Ema chatbot."""

import gradio as gr
from dotenv import load_dotenv

from .bot import BareGeminiBot, PrettyGeminiBot, SimpleBot
from .ui import ChatUI


# Load environment variables from .env file
load_dotenv()


def main():
    """Main entry point for Mini Ema chat application."""
    # Create bot instances
    bots = {
        "Simple Bot": SimpleBot(),
        "Bare Gemini Bot": BareGeminiBot(),
        "Pretty Gemini Bot": PrettyGeminiBot(),
    }

    # Create and launch the chat UI
    chat_ui = ChatUI(bots)
    chat_ui.launch(theme=gr.themes.Default())


if __name__ == "__main__":
    main()
