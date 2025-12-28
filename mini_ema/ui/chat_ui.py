"""Chat UI components for Mini Ema."""

import os
import re
import time

import gradio as gr

from ..bot.base import BaseBot


# Streaming configuration
STREAMING_DELAY = 0.02  # Delay between characters in seconds

# Avatar images - configurable via environment variables
USER_AVATAR = os.getenv("USER_AVATAR", "assets/imgs/user.png")
EMA_AVATAR = os.getenv("EMA_AVATAR", "assets/imgs/ema.png")

# Expression images directory
EXPRESSION_IMGS_DIR = os.getenv("EXPRESSION_IMGS_DIR", "assets/gen_imgs")


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
        self.current_expression = "neutral"
        self.current_action = "none"

    def _user_message(self, user_message: str, history: list):
        """Add user message to history.

        Args:
            user_message: User's message
            history: Chat history

        Returns:
            Tuple of (empty string, updated history)
        """
        return "", history + [{"role": "user", "content": user_message}]

    def _parse_expression_and_action(self, content: str) -> tuple[str, str]:
        """Parse expression and action from AI response content.

        Args:
            content: The AI response content

        Returns:
            Tuple of (expression, action)
        """
        # Default values
        expression = "neutral"
        action = "none"

        # Try to match expression pattern: [Expression: <expression>]
        expression_match = re.search(r"\[Expression:\s*(\w+)\]", content, re.IGNORECASE)
        if expression_match:
            expression = expression_match.group(1).lower()

        # Try to match action pattern: [Action: <action>]
        action_match = re.search(r"\[Action:\s*(\w+)\]", content, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).lower()

        return expression, action

    def _get_expression_image_path(self, expression: str, action: str) -> str:
        """Get the path to the expression image.

        Args:
            expression: The facial expression
            action: The physical action

        Returns:
            Path to the expression image file, or default avatar if not found
        """
        # Build the image filename
        image_filename = f"{expression}_{action}.jpg"
        image_path = os.path.join(EXPRESSION_IMGS_DIR, image_filename)

        # Check if the image exists
        if os.path.exists(image_path):
            return image_path
        else:
            # Fallback to default avatar
            return EMA_AVATAR

    def _bot_response(self, history: list, selected_bot: str, username: str):
        """Generate AI response with streaming.

        Args:
            history: Chat history
            selected_bot: Name of the selected bot
            username: The name of the user

        Yields:
            Tuple of (updated history, expression image path)
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
                # Case 2: content is a list like [{'text': 'hello', 'type': 'text'}]
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
                # Parse expression and action from the current content
                expression, action = self._parse_expression_and_action(history[-1]["content"])
                image_path = self._get_expression_image_path(expression, action)
                yield history, image_path

            # Final yield with complete content
            expression, action = self._parse_expression_and_action(content)
            self.current_expression = expression
            self.current_action = action
            image_path = self._get_expression_image_path(expression, action)
            yield history, image_path

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio chat interface.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks() as demo:
            gr.Markdown("# 💬 Mini Ema Chat")

            with gr.Row():
                with gr.Column(scale=3):
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
                        label="👤 Username",
                        placeholder="Enter username...",
                        interactive=True,
                    )

                with gr.Column(scale=1):
                    # Expression display
                    expression_image = gr.Image(
                        value=self._get_expression_image_path("neutral", "none"),
                        label="💫 Ema's Expression",
                        height=300,
                        show_label=True,
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
                # Reset expression to default
                default_image = self._get_expression_image_path("neutral", "none")
                return [], default_image

            # Handle message sending with streaming
            msg_input.submit(self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                self._bot_response, [chatbot, bot_selector, username_input], [chatbot, expression_image]
            )

            send_btn.click(self._user_message, [msg_input, chatbot], [msg_input, chatbot], queue=False).then(
                self._bot_response, [chatbot, bot_selector, username_input], [chatbot, expression_image]
            )

            clear.click(clear_chat, bot_selector, [chatbot, expression_image], queue=False)

            # When bot selector changes, clear the chat
            bot_selector.change(clear_chat, bot_selector, [chatbot, expression_image], queue=False)

        return demo

    def launch(self, **kwargs):
        """Launch the chat interface.

        Args:
            **kwargs: Additional arguments to pass to demo.launch()
        """
        demo = self.create_interface()
        demo.launch(**kwargs)
