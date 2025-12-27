"""Main entry point for Mini Ema chatbot."""

import gradio as gr

from mini_ema.bot import SimpleBot
from mini_ema.ui import ChatUI


def main():
    """Main entry point for Mini Ema chat application."""
    # Initialize the bot
    bot = SimpleBot()

    # Create and launch the chat UI
    chat_ui = ChatUI(bot)
    chat_ui.launch(theme=gr.themes.Default())


if __name__ == "__main__":
    main()
