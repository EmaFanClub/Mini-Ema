"""Main entry point for Mini Ema chatbot."""

import time
import gradio as gr

# Streaming configuration
STREAMING_DELAY = 0.02  # Delay between characters in seconds

# Avatar images - using dicebear API for initials
USER_AVATAR = "https://api.dicebear.com/9.x/initials/svg?seed=User"
EMA_AVATAR = "https://api.dicebear.com/9.x/initials/svg?seed=Ema"


def get_ai_response(message: str) -> list[dict]:
    """Get hardcoded AI response as structured messages.
    
    Args:
        message: User message (unused in hardcoded version)
        
    Returns:
        List of message dictionaries with role, content, and optional metadata
    """
    # Return two example responses with structured format
    return [
        {
            "role": "assistant",
            "content": "你好，我是Ema。",
            "metadata": {"title": "💭 Thinking: 我是Ema"}
        },
        {
            "role": "assistant", 
            "content": "有什么可以帮助你的吗？",
            "metadata": {"title": "💭 Thinking: 很高兴认识你"}
        }
    ]


def user(user_message: str, history: list):
    """Add user message to history.
    
    Args:
        user_message: User's message
        history: Chat history
        
    Returns:
        Tuple of (empty string, updated history)
    """
    return "", history + [{"role": "user", "content": user_message}]


def bot(history: list):
    """Generate AI response with streaming.
    
    Args:
        history: Chat history
        
    Yields:
        Updated history with streaming AI response
    """
    # Get the AI response as structured messages
    ai_messages = get_ai_response(history[-1]["content"] if history else "")
    
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
            time.sleep(STREAMING_DELAY)
            yield history


def create_ui():
    """Create and launch the chat UI."""
    with gr.Blocks() as demo:
        gr.Markdown("# 💬 Mini Ema Chat")
        
        chatbot = gr.Chatbot(
            value=[],
            height=600,
            avatar_images=(
                USER_AVATAR,  # User avatar from dicebear initials
                EMA_AVATAR    # Ema avatar from dicebear initials
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
            user, 
            [msg_input, chatbot], 
            [msg_input, chatbot], 
            queue=False
        ).then(
            bot, 
            chatbot, 
            chatbot
        )
        
        send_btn.click(
            user, 
            [msg_input, chatbot], 
            [msg_input, chatbot], 
            queue=False
        ).then(
            bot, 
            chatbot, 
            chatbot
        )
        
        clear.click(lambda: None, None, chatbot, queue=False)
    
    return demo


def main():
    """Main entry point."""
    demo = create_ui()
    demo.launch(theme=gr.themes.Default())


if __name__ == "__main__":
    main()
