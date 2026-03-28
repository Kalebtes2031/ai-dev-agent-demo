from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional


_PY_GITIGNORE = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/

# Distribution / packaging
build/
dist/
*.egg-info/

# Unit test / coverage reports
.coverage
.pytest_cache/

# IDE / editor
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
"""


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def _increment_day(readme_path: Path) -> Optional[int]:
    if not readme_path.exists():
        return None

    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    updated = False
    new_day = None

    for line in lines:
        if not updated and line.strip().lower().startswith("day "):
            parts = line.strip().split()
            try:
                current = int(parts[-1])
            except ValueError:
                current = 0
            new_day = current + 1
            new_lines.append(f"Day {new_day}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_day = 1
        new_lines.append(f"Day {new_day}")

    readme_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    return new_day


def _ensure_main_placeholder(main_path: Path) -> None:
    if not main_path.exists():
        return

    content = main_path.read_text(encoding="utf-8")
    marker = "# TODO: AI-generated enhancements go here\n"
    if marker in content:
        return

    updated = content.rstrip() + "\n\n" + marker
    main_path.write_text(updated, encoding="utf-8")


def generate_project(project_name: str, description: str) -> Path:
    base = Path("ai_dev_agent") / "projects" / project_name
    base.mkdir(parents=True, exist_ok=True)

    day_number = date.today().timetuple().tm_yday

    main_py = """def main() -> None:
    print(\"Hello from {name}!\")


if __name__ == \"__main__\":
    main()
""".format(
        name=project_name
    )

    readme = f"""# {project_name}

{description}

Day {day_number}
"""

    _write_if_missing(base / "main.py", main_py)
    _write_if_missing(base / "README.md", readme)
    _write_if_missing(base / ".gitignore", _PY_GITIGNORE)

    return base


def continue_project(project_name: str) -> Optional[int]:
    base = Path("ai_dev_agent") / "projects" / project_name
    if not base.exists():
        return None

    new_day = _increment_day(base / "README.md")
    _ensure_main_placeholder(base / "main.py")
    return new_day
