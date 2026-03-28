from __future__ import annotations

from pathlib import Path
from typing import Optional


_LAST_PROJECT_FILE = Path("ai_dev_agent") / "data" / "last_project.txt"


def set_last_project(project_name: str) -> None:
    _LAST_PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _LAST_PROJECT_FILE.write_text(project_name.strip() + "\n", encoding="utf-8")


def get_last_project() -> Optional[str]:
    if not _LAST_PROJECT_FILE.exists():
        return None

    value = _LAST_PROJECT_FILE.read_text(encoding="utf-8").strip()
    return value or None
