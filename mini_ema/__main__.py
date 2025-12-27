"""Main entry point for Mini Ema chatbot."""

import re
import time
import gradio as gr
from gradio import ChatMessage

# Streaming configuration
STREAMING_DELAY = 0.02  # Delay between characters in seconds

# Styling constants
THINKING_STYLE = 'color: #6B7280; font-style: italic; margin-bottom: 8px;'
ANSWER_STYLE = 'color: #1F2937;'


def parse_ai_responses(response: str) -> list[tuple[str, str]]:
    """Parse AI response into multiple message parts.
    
    Each response can have multiple <think>/<answer> pairs, creating separate bubbles.
    
    Args:
        response: AI response string with <think> and <answer> tags
        
    Returns:
        List of (thinking, answer) tuples for each message bubble
    """
    # Find all think/answer pairs using regex
    messages = []
    
    # Pattern to match think/answer pairs - at least one tag must be present
    pattern = r'<think>(.*?)</think>(?:<answer>(.*?)</answer>)?|<answer>(.*?)</answer>'
    matches = re.finditer(pattern, response, re.DOTALL)
    
    for match in matches:
        # Handle <think>...</think><answer>...</answer> pattern
        if match.group(1) is not None:
            thinking = match.group(1).strip()
            answer = match.group(2).strip() if match.group(2) else ""
        # Handle standalone <answer>...</answer> pattern
        else:
            thinking = ""
            answer = match.group(3).strip() if match.group(3) else ""
        
        if thinking or answer:
            messages.append((thinking, answer))
    
    return messages if messages else [("", "")]


def get_ai_response(message: str) -> str:
    """Get hardcoded AI response.
    
    Args:
        message: User message (unused in hardcoded version)
        
    Returns:
        Hardcoded AI response (can contain multiple messages)
    """
    return "<think>我是Ema</think><answer>你好，我是Ema。</answer>"


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
    # Get the AI response
    ai_response = get_ai_response(history[-1]["content"] if history else "")
    
    # Parse into multiple messages
    messages = parse_ai_responses(ai_response)
    
    # Stream each message
    for thinking, answer in messages:
        # Add thinking part with streaming
        if thinking:
            history.append({"role": "assistant", "content": ""})
            thinking_prefix = f'<div style="{THINKING_STYLE}">💭 '
            history[-1]["content"] = thinking_prefix
            for char in thinking:
                history[-1]["content"] += char
                time.sleep(STREAMING_DELAY)
                yield history
            history[-1]["content"] += '</div>'
            yield history
        
        # Add answer part with streaming
        if answer:
            if not thinking:
                history.append({"role": "assistant", "content": ""})
            
            answer_prefix = f'<div style="{ANSWER_STYLE}">'
            if thinking:
                history[-1]["content"] += answer_prefix
            else:
                history[-1]["content"] = answer_prefix
                
            for char in answer:
                history[-1]["content"] += char
                time.sleep(STREAMING_DELAY)
                yield history
            history[-1]["content"] += '</div>'
            yield history


def create_ui():
    """Create and launch the chat UI."""
    with gr.Blocks() as demo:
        gr.Markdown("# 💬 Mini Ema Chat")
        
        chatbot = gr.Chatbot(
            value=[],
            height=600,
            avatar_images=(
                None,  # User avatar - will use default
                None   # Ema avatar - will use default
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
    demo.launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
