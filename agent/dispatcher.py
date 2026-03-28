# agent/dispatcher.py
"""Dispatch parsed actions into project operations."""

from __future__ import annotations

import subprocess

from executor.codegen import continue_project, generate_project
from executor.git_handler import create_and_push_project, init_repo, commit_changes, push_changes
from executor.project_state import get_last_project, set_last_project

from .command_parser import Action


def _split_new_args(args: list[str]) -> tuple[str | None, str]:
    if not args:
        return None, ""
    name = args[0].strip()
    description = " ".join(args[1:]).strip()
    return name, description


def _get_target_project(args: list[str]) -> str | None:
    if args:
        return args[0].strip()
    return get_last_project()


def dispatch_action(action: Action) -> None:
    try:
        if action.name == "create_project":
            project_name, description = _split_new_args(action.args)
            if not project_name:
                print("/new requires a project name")
                return

            generate_project(project_name, description)
            set_last_project(project_name)
            create_and_push_project("ai_dev_agent/projects", project_name, "Initial commit")
            print(f"Project '{project_name}' created and pushed")
            return

        if action.name == "continue_project":
            project_name = _get_target_project(action.args)
            if not project_name:
                print("/continue requires a project name or a previous /new")
                return

            new_day = continue_project(project_name)
            if new_day is None:
                print(f"Project '{project_name}' not found")
                return

            repo_url = f"git@github-mekonnen:Mekonnen44/{project_name}.git"
            repo_path = f"ai_dev_agent/projects/{project_name}"
            init_repo(repo_path, repo_url=repo_url)
            commit_changes(repo_path, f"Day {new_day} update")
            push_changes(repo_path)
            set_last_project(project_name)
            print(f"Project '{project_name}' advanced to Day {new_day}")
            return

        if action.name == "push_code":
            print("/push is not wired yet")
            return

        print(f"Action: {action.name} args={action.args} raw={action.raw}")
    except subprocess.CalledProcessError as exc:
        print(f"Git command failed: {exc}")
