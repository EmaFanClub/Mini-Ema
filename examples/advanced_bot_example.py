"""Example: Creating a custom bot with complex response strategy.

This example demonstrates how to create a custom bot implementation
that uses more sophisticated logic for generating responses.
"""

from mini_ema.bot import BaseBot


class AdvancedBot(BaseBot):
    """An advanced bot with more complex response strategy.

    This bot demonstrates how to implement custom logic for:
    - Context-aware responses based on chat history
    - Multiple thinking steps
    - Dynamic response generation
    """

    def __init__(self, enable_thinking: bool = True):
        """Initialize the advanced bot.

        Args:
            enable_thinking: Whether to include thinking metadata in responses
        """
        self.enable_thinking = enable_thinking

    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        """Generate response using advanced strategy.

        Args:
            message: User message
            history: Chat history for context

        Returns:
            List of message dictionaries with role, content, and optional metadata
        """
        # Example: Analyze message and history to determine response
        history = history or []

        # Count previous messages
        msg_count = len([h for h in history if h.get("role") == "user"])

        responses = []

        # First response: Acknowledge the message
        if self.enable_thinking:
            responses.append({
                "role": "assistant",
                "content": f"我收到了你的消息: '{message}'",
                "metadata": {"title": "💭 Thinking: 分析用户输入"},
            })

        # Second response: Context-aware reply
        if msg_count == 0:
            content = "这是我们的第一次对话，很高兴认识你！"
            thinking = "这是第一条消息"
        elif msg_count < 3:
            content = f"这是我们的第 {msg_count + 1} 次交流。"
            thinking = f"已经交流了 {msg_count} 次"
        else:
            content = "我们已经聊了很多了！"
            thinking = "对话历史较长"

        responses.append({
            "role": "assistant",
            "content": content,
            "metadata": {"title": f"💭 Thinking: {thinking}"} if self.enable_thinking else None,
        })

        # Third response: Message-specific response
        if "你好" in message or "hello" in message.lower():
            responses.append({
                "role": "assistant",
                "content": "你好！有什么可以帮助你的吗？",
                "metadata": {"title": "💭 Thinking: 检测到问候语"} if self.enable_thinking else None,
            })
        elif "?" in message or "？" in message or "吗" in message:
            responses.append({
                "role": "assistant",
                "content": "这是一个很好的问题！让我思考一下...",
                "metadata": {"title": "💭 Thinking: 检测到问题"} if self.enable_thinking else None,
            })

        return responses


# Example usage
if __name__ == "__main__":
    import gradio as gr

    from mini_ema.ui import ChatUI

    # Create an advanced bot instance
    bot = AdvancedBot(enable_thinking=True)

    # Create and launch the UI with the custom bot
    chat_ui = ChatUI(bot)
    chat_ui.launch(theme=gr.themes.Default())
