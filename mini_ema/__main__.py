"""Main entry point for Mini Ema chatbot."""

import re
import gradio as gr
from gradio import ChatMessage


def parse_ai_response(response: str) -> tuple[str, str]:
    """Parse AI response into thinking and answer parts.
    
    Args:
        response: AI response string with <think> and <answer> tags
        
    Returns:
        Tuple of (thinking, answer) strings
    """
    think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    answer_match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL)
    
    thinking = think_match.group(1).strip() if think_match else ""
    answer = answer_match.group(1).strip() if answer_match else ""
    
    return thinking, answer


def get_ai_response(message: str) -> str:
    """Get hardcoded AI response.
    
    Args:
        message: User message (unused in hardcoded version)
        
    Returns:
        Hardcoded AI response
    """
    return "<think>我是Ema</think><answer>你好，我是Ema。</answer>"


def chat(message: str, history: list) -> tuple[str, list]:
    """Process chat message and update history.
    
    Args:
        message: User's message
        history: Chat history in ChatMessage format
        
    Returns:
        Tuple of (empty string, updated history)
    """
    if not message.strip():
        return "", history
    
    # Add user message
    history.append(ChatMessage(role="user", content=message))
    
    # Get AI response
    ai_response = get_ai_response(message)
    thinking, answer = parse_ai_response(ai_response)
    
    # Format AI response with colored parts
    formatted_response = ""
    if thinking:
        formatted_response += f'<div style="color: #6B7280; font-style: italic; margin-bottom: 8px;">💭 {thinking}</div>'
    if answer:
        formatted_response += f'<div style="color: #1F2937;">{answer}</div>'
    
    # Add AI response
    history.append(ChatMessage(role="assistant", content=formatted_response))
    
    return "", history


def create_ui():
    """Create and launch the chat UI."""
    with gr.Blocks() as demo:
        gr.Markdown("# 💬 Mini Ema Chat")
        
        state = gr.State([])
        
        chatbot = gr.Chatbot(
            value=[],
            height=600,
            avatar_images=(
                "https://api.dicebear.com/7.x/avataaars/svg?seed=User",
                "https://api.dicebear.com/7.x/avataaars/svg?seed=Ema"
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
        
        def update_chat(message, history):
            """Update chat and return formatted history."""
            new_message, new_history = chat(message, history)
            return new_message, new_history, new_history
        
        # Handle message sending
        msg_input.submit(
            update_chat,
            inputs=[msg_input, state],
            outputs=[msg_input, state, chatbot],
        )
        send_btn.click(
            update_chat,
            inputs=[msg_input, state],
            outputs=[msg_input, state, chatbot],
        )
    
    return demo


def main():
    """Main entry point."""
    demo = create_ui()
    demo.launch(
        theme=gr.themes.Soft(),
        css="""
        .message-row {
            margin: 8px 0;
        }
        """
    )


if __name__ == "__main__":
    main()
