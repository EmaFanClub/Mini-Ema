"""Bot module for Mini Ema.

This module provides the AI bot functionality for generating responses.
It includes base classes and implementations for different bot strategies.
"""

from .base import BaseBot
from .gemini_bot import BareGeminiBot
from .simple_bot import SimpleBot


__all__ = ["BareGeminiBot", "BaseBot", "SimpleBot"]
