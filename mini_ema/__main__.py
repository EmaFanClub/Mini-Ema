"""Main entry point for Mini Ema chatbot."""

import gradio as gr

from .bot import SimpleBot
from .ui import ChatUI


def main():
    """Main entry point for Mini Ema chat application."""
    # Initialize the bot
    bot = SimpleBot()

    # Create and launch the chat UI
    chat_ui = ChatUI(bot)
    chat_ui.launch(theme=gr.themes.Default())


if __name__ == "__main__":
    main()
