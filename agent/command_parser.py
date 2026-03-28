# agent/command_parser.py
"""Parse bot commands into structured actions."""

from dataclasses import dataclass
from typing import List, Optional

from bot.models import Command


@dataclass(frozen=True)
class Action:
    name: str
    args: List[str]
    raw: str


_COMMAND_TO_ACTION = {
    "new": "create_project",
    "continue": "continue_project",
    "push": "push_code",
}


def parse_action(command: Command) -> Optional[Action]:
    action_name = _COMMAND_TO_ACTION.get(command.name)
    if not action_name:
        return None

    return Action(name=action_name, args=command.args, raw=command.raw)
