# Examples

This directory contains example implementations showing how to extend Mini Ema with custom bot strategies.

## Examples

### 1. Advanced Bot Example (`advanced_bot_example.py`)

Demonstrates a custom bot with complex response logic:
- Context-aware responses based on chat history
- Multiple thinking steps
- Dynamic message generation

**Run it:**
```bash
python examples/advanced_bot_example.py
```

### 2. Gemini Bot Example (`gemini_bot_example.py`)

Shows how to integrate with Google Gemini API:
- Uses real AI model for responses
- Handles API errors gracefully
- Demonstrates external service integration

**Requirements:**
```bash
pip install google-genai
```

**Setup:**
```bash
export GEMINI_API_KEY="your-api-key"
python examples/gemini_bot_example.py
```

## Creating Your Own Bot

All bots must inherit from `BaseBot` and implement the `get_response` method:

```python
from mini_ema.bot import BaseBot

class MyBot(BaseBot):
    def get_response(self, message: str, history: list | None = None) -> list[dict]:
        # Your logic here
        return [
            {
                "role": "assistant",
                "content": "Your response",
                "metadata": {"title": "💭 Optional thinking"}  # optional
            }
        ]
```

See the main README for more details.
