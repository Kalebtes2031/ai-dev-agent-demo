from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class Message:
    chat_id: str
    text: str
    user_id: str
    role: MessageRole = MessageRole.USER


@dataclass(frozen=True)
class Command:
    name: str
    args: List[str]
    raw: str

    @property
    def is_known(self) -> bool:
        return self.name in {"start", "new", "continue", "push"}


@dataclass(frozen=True)
class ParsedInput:
    message: Message
    command: Optional[Command]
