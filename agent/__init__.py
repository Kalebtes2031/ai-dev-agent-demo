# agent/__init__.py
"""Agent package for command parsing and action dispatching."""

from .command_parser import parse_action
from .dispatcher import dispatch_action

__all__ = ["parse_action", "dispatch_action"]
