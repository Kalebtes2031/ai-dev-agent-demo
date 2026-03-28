# bot/dispatcher.py
"""Routes parsed commands to handlers and agent actions."""

from agent import dispatch_action, parse_action

from . import handlers
from .models import Command, Message


def dispatch(message: Message, command: Command) -> None:
    mapping = {
        "start": handlers.handle_start,
        "new": handlers.handle_new,
        "continue": handlers.handle_continue,
        "push": handlers.handle_push,
    }

    handler = mapping.get(command.name, handlers.handle_unknown)
    handler(message, command)

    action = parse_action(command)
    if action:
        dispatch_action(action)
