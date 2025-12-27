"""Chat UI components for Mini Ema."""

import time

import gradio as gr

from mini_ema.bot.base import BaseBot


# Streaming configuration
STREAMING_DELAY = 0.02  # Delay between characters in seconds

# Avatar images - using dicebear API for initials
USER_AVATAR = "https://api.dicebear.com/9.x/initials/svg?seed=User"
EMA_AVATAR = "https://api.dicebear.com/9.x/initials/svg?seed=Ema"


class ChatUI:
    """Gradio-based chat interface for Mini Ema.

    This class encapsulates the chat UI logic and provides a clean interface
    for creating and launching the chat application.
    """

    def __init__(self, bot: BaseBot, streaming_delay: float = STREAMING_DELAY):
        """Initialize the chat UI.

        Args:
            bot: The bot instance to use for generating responses
            streaming_delay: Delay between characters when streaming (seconds)
        """
        self.bot = bot
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

    def _bot_response(self, history: list):
        """Generate AI response with streaming.

        Args:
            history: Chat history

        Yields:
            Updated history with streaming AI response
        """
        # Get the AI response as structured messages
        user_msg = history[-1]["content"] if history else ""
        ai_messages = self.bot.get_response(user_msg, history)

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

            chatbot = gr.Chatbot(
                value=[],
                height=600,
                avatar_images=(
                    USER_AVATAR,  # User avatar from dicebear initials
                    EMA_AVATAR,  # Ema avatar from dicebear initials
                ),
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

            # Handle message sending with streaming
            msg_input.submit(
                self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False
            ).then(self._bot_response, chatbot, chatbot)

            send_btn.click(
                self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False
            ).then(self._bot_response, chatbot, chatbot)

            clear.click(lambda: None, None, chatbot, queue=False)

        return demo

    def launch(self, **kwargs):
        """Launch the chat interface.

        Args:
            **kwargs: Additional arguments to pass to demo.launch()
        """
        demo = self.create_interface()
        demo.launch(**kwargs)
