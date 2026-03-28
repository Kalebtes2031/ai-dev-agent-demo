# bot/parser.py
"""Parsing utilities for Telegram-style commands."""

from typing import List, Optional

from .models import Command


def _tokenize(text: str) -> List[str]:
    return [t for t in text.strip().split() if t]


def parse_command(text: str) -> Optional[Command]:
    tokens = _tokenize(text)
    if not tokens:
        return None

    head = tokens[0]
    if not head.startswith("/"):
        return None

    name = head[1:]
    if not name:
        return None

    return Command(name=name, args=tokens[1:], raw=text)
