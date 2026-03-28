# bot/handlers.py
"""Command handlers. Business logic intentionally not implemented."""

from .models import Command, Message


def handle_start(message: Message, command: Command) -> None:
    print(f"/start received from user={message.user_id} chat={message.chat_id} args={command.args}")


def handle_new(message: Message, command: Command) -> None:
    print(f"/new received from user={message.user_id} chat={message.chat_id} args={command.args}")


def handle_continue(message: Message, command: Command) -> None:
    print(f"/continue received from user={message.user_id} chat={message.chat_id} args={command.args}")


def handle_push(message: Message, command: Command) -> None:
    print(f"/push received from user={message.user_id} chat={message.chat_id} args={command.args}")


def handle_unknown(message: Message, command: Command) -> None:
    print(f"Unknown command '/{command.name}' from user={message.user_id} chat={message.chat_id} args={command.args}")


def handle_message(message: Message) -> None:
    print(f"Message received from user={message.user_id} chat={message.chat_id}: {message.text}")
