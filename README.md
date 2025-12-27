# Mini Ema

A simple chatbot UI built with Gradio, featuring multiple AI bot implementations.

## Installation

```bash
uv sync
```

## Configuration

To use the Gemini LLM bot, you need to configure your API key:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-3-flash-preview
   ```

Get your API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).

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
│   ├── simple_bot.py    # SimpleBot implementation (hardcoded responses)
│   ├── bare_gemini_bot.py  # BareGeminiBot implementation (Google Gemini API)
│   └── pretty_gemini_bot.py  # PrettyGeminiBot implementation (Structured outputs)
└── ui/                  # UI module - Gradio interface components
    ├── __init__.py      # UI module exports
    └── chat_ui.py       # ChatUI class and interface logic
```

## Features

- WhatsApp-style chat interface
- User messages on the right, AI responses on the left
- Avatar images for User and Ema
- **Bot selector dropdown** to switch between different AI bots
- **User name input** to personalize interactions (default: "Phoenix")
- AI responses show metadata including:
  - Response title with emoji
  - Finish reason
  - Model version
  - Token usage breakdown (prompt, response, thinking, total)
- Input is disabled while waiting for AI response
- Modular architecture with pluggable bot implementations

## Available Bots

### Simple Bot
A demo bot with hardcoded responses for testing the UI.

### Bare Gemini Bot
AI-powered bot using Google's Gemini API with the `gemini-3-flash-preview` model. Features:
- Real-time AI responses
- Detailed usage metadata
- Environment-based configuration
- Error handling for API issues

### Pretty Gemini Bot
Advanced AI-powered bot using Gemini's Structured Outputs capability. Features:
- Character personality: Kristina, an 18-year-old genius scientist with a tsundere personality
- Research focus: AI and large language models
- Structured output format with:
  - Internal thoughts (think)
  - Facial expressions (neutral, smile, serious, confused, surprised, sad)
  - Physical actions (none, nod, shake, wave, jump, point)
  - Spoken words (speak)
- Multi-language support (responds in the same language as user input)
- User name addressing via XML tags
- Emoji-based expression indicators in chat bubbles
