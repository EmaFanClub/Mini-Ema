"""Chat UI components for Mini Ema."""

import os
import time

import gradio as gr

from ..bot.base import BaseBot


# Streaming configuration
STREAMING_DELAY = 0.02  # Delay between characters in seconds

# Avatar images - configurable via environment variables
USER_AVATAR = os.getenv("USER_AVATAR", "assets/imgs/user.png")
EMA_AVATAR = os.getenv("EMA_AVATAR", "assets/imgs/ema.png")


class ChatUI:
    """Gradio-based chat interface for Mini Ema.

    This class encapsulates the chat UI logic and provides a clean interface
    for creating and launching the chat application.
    """

    def __init__(self, bots: dict[str, BaseBot], streaming_delay: float = STREAMING_DELAY):
        """Initialize the chat UI.

        Args:
            bots: Dictionary of bot name -> bot instance
            streaming_delay: Delay between characters when streaming (seconds)
        """
        self.bots = bots
        self.streaming_delay = streaming_delay

    def _user_message(self, user_message: str, history: list):
        """Add user message to history.

        Args:
            user_message: User's message
            history: Chat history

        Returns:
            Tuple of (empty string, updated history)
        """
        return "", history + [{"role": "user", "content": user_message}]

    def _bot_response(self, history: list, selected_bot: str, username: str):
        """Generate AI response with streaming.

        Args:
            history: Chat history
            selected_bot: Name of the selected bot
            username: The name of the user

        Yields:
            Updated history with streaming AI response
        """
        # Get the selected bot instance
        current_bot = self.bots.get(selected_bot, next(iter(self.bots.values())))

        # Get the AI response as an iterable of structured messages
        # Extract user message - handle both string and list formats
        user_msg = ""
        if history:
            content = history[-1]["content"]
            if isinstance(content, str):
                # Case 1: content is a string
                user_msg = content
            elif isinstance(content, list):
                # Case 2: content is a list like [{'text': 'da', 'type': 'text'}]
                # Extract text from all items in the list
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        text_parts.append(item["text"])
                user_msg = " ".join(text_parts)
            else:
                user_msg = str(content)

        ai_messages = current_bot.get_response(user_msg, username)

        # Stream each message as a separate bubble
        for msg in ai_messages:
            # Create a new bubble for each message
            new_message = {"role": "assistant", "content": ""}

            # Add metadata if present
            if "metadata" in msg:
                new_message["metadata"] = msg["metadata"]

            history.append(new_message)

            # Stream the content character by character
            content = msg.get("content", "")
            for char in content:
                history[-1]["content"] += char
                time.sleep(self.streaming_delay)
                yield history

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio chat interface.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks() as demo:
            gr.Markdown("# 💬 Mini Ema Chat")

            # Bot selector
            bot_selector = gr.Dropdown(
                choices=list(self.bots.keys()),
                value=list(self.bots.keys())[0],
                label="🤖 Select Bot",
                interactive=True,
            )

            # User name input
            username_input = gr.Textbox(
                value="Phoenix",
                label="👤 User Name",
                placeholder="Enter user name...",
                interactive=True,
            )

            chatbot = gr.Chatbot(
                value=[],
                height=600,
                avatar_images=(USER_AVATAR, EMA_AVATAR),
                show_label=False,
            )

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Type your message here...",
                    show_label=False,
                    scale=9,
                    container=False,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            clear = gr.Button("Clear")

            def clear_chat(selected_bot):
                """Clear chat history and reset bot."""
                # Call clear method on the selected bot if it exists
                bot = self.bots.get(selected_bot)
                if bot and hasattr(bot, "clear"):
                    bot.clear()
                return []

            # Handle message sending with streaming
            msg_input.submit(self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                self._bot_response, [chatbot, bot_selector, username_input], chatbot
            )

            send_btn.click(self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                self._bot_response, [chatbot, bot_selector, username_input], chatbot
            )

            clear.click(clear_chat, bot_selector, chatbot, queue=False)

            # When bot selector changes, clear the chat
            bot_selector.change(clear_chat, bot_selector, chatbot, queue=False)

        return demo

    def launch(self, **kwargs):
        """Launch the chat interface.

        Args:
            **kwargs: Additional arguments to pass to demo.launch()
        """
        demo = self.create_interface()
        demo.launch(**kwargs)
