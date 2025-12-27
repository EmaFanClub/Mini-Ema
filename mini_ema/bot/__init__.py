"""Bot module for Mini Ema.

This module provides the AI bot functionality for generating responses.
It includes base classes and implementations for different bot strategies.
"""

from mini_ema.bot.base import BaseBot
from mini_ema.bot.simple_bot import SimpleBot


__all__ = ["BaseBot", "SimpleBot"]
