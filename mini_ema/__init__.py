"""Mini Ema - A simple chatbot UI.

A modular chatbot framework with pluggable bot implementations
and a Gradio-based chat interface.
"""

from mini_ema.bot import BaseBot, SimpleBot
from mini_ema.ui import ChatUI


__version__ = "0.1.0"
__all__ = ["BaseBot", "SimpleBot", "ChatUI"]
