# Mini Ema

A simple chatbot UI built with Gradio.

## Installation

```bash
uv sync
```

## Usage

Launch the chatbot UI:

```bash
uv run python -m mini_ema
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

## Features

- WhatsApp-style chat interface
- User messages on the right, AI responses on the left
- Avatar images for User and Ema
- AI responses show thinking and answer parts with different colors
- Input is disabled while waiting for AI response
- Modular architecture with pluggable bot implementations
