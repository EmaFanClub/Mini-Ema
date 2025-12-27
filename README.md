# Mini Ema

A modular chatbot framework built with Gradio, featuring pluggable bot implementations and a clean chat interface.

## Installation

```bash
pip install -e .
```

## Usage

Launch the chatbot UI:

```bash
python -m mini_ema
```

The application will start a web server and open the chat interface in your browser.

## Project Structure

```
mini_ema/
├── __init__.py          # Package initialization and main exports
├── __main__.py          # Entry point for running the application
├── bot/                 # Bot module - AI response generation
│   ├── __init__.py      # Bot module exports
│   ├── base.py          # BaseBot abstract interface
│   └── simple_bot.py    # SimpleBot implementation (hardcoded responses)
└── ui/                  # UI module - Gradio interface components
    ├── __init__.py      # UI module exports
    └── chat_ui.py       # ChatUI class and interface logic
```

## Architecture

The project is organized into three main components:

### 1. Bot Module (`mini_ema/bot/`)
Handles AI response generation with a pluggable architecture:
- **BaseBot**: Abstract base class defining the bot interface
- **SimpleBot**: Basic implementation with hardcoded responses
- **Extensible**: Easy to add new bot implementations with different strategies

### 2. UI Module (`mini_ema/ui/`)
Manages the Gradio chat interface:
- **ChatUI**: Main chat interface class
- Handles message streaming and display
- Configurable avatars and styling

### 3. Entry Point (`__main__.py`)
Minimal entry point that:
- Initializes the bot
- Creates the UI
- Launches the application

## Creating Custom Bots

To create a custom bot with your own response strategy:

```python
from mini_ema.bot import BaseBot

class MyCustomBot(BaseBot):
    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        # Your custom logic here
        return [
            {
                "role": "assistant",
                "content": "Your response",
                "metadata": {"title": "💭 Thinking: ..."}  # optional
            }
        ]
```

Then use it in your application:

```python
from mini_ema.ui import ChatUI
from my_bot import MyCustomBot

bot = MyCustomBot()
chat_ui = ChatUI(bot)
chat_ui.launch()
```

## Features

- WhatsApp-style chat interface
- User messages on the right, AI responses on the left
- Avatar images for User and Ema
- AI responses show thinking and answer parts with different colors
- Streaming text output with configurable delay
- Input is disabled while waiting for AI response
- Modular architecture for easy extensibility
