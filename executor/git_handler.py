import subprocess
import os
from pathlib import Path
from typing import List, Optional

def _run(cmd: List[str], cwd: Path) -> None:
    try:
        subprocess.run(cmd, cwd=str(cwd), check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Git execution failed: {e.stderr}")
        raise

def _run_capture(cmd: List[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=str(cwd), check=True, capture_output=True, text=True)
    return result.stdout.strip()

def _has_changes(path: Path) -> bool:
    try:
        status = _run_capture(["git", "status", "--porcelain"], path)
        return bool(status)
    except subprocess.CalledProcessError:
        return False

def _ensure_remote(path: Path, repo_url: str) -> None:
    try:
        existing = _run_capture(["git", "remote", "get-url", "origin"], path)
    except subprocess.CalledProcessError:
        existing = ""

    if not existing:
        _run(["git", "remote", "add", "origin", repo_url], path)
        return

    if existing != repo_url:
        _run(["git", "remote", "set-url", "origin", repo_url], path)

def init_repo(path: str, repo_url: Optional[str] = None) -> None:
    repo_path = Path(path).resolve()
    repo_path.mkdir(parents=True, exist_ok=True)

    git_dir = repo_path / ".git"
    if not git_dir.exists():
        _run(["git", "init"], repo_path)

    if repo_url:
        _ensure_remote(repo_path, repo_url)

def commit_changes(path: str, message: str) -> None:
    repo_path = Path(path).resolve()
    _run(["git", "add", "."], repo_path)
    if _has_changes(repo_path):
        _run(["git", "commit", "-m", message], repo_path)

def push_changes(path: str) -> None:
    repo_path = Path(path).resolve()
    
    # HARDEN: Set local identity as safety net
    username = os.getenv("GITHUB_USERNAME", "Mekonnen44")
    _run(["git", "config", "user.name", username], repo_path)
    _run(["git", "config", "user.email", "Mekonnentsehaye44@gmail.com"], repo_path)
    
    _run(["git", "branch", "-M", "main"], repo_path)
    # HARDEN: Use force-push to handle remote desyncs
    _run(["git", "push", "-u", "origin", "main", "--force"], repo_path)

def repo_exists(path: str) -> bool:
    return (Path(path).resolve() / ".git").exists()

def init_or_validate_repo(path: str, repo_url: str) -> None:
    if not repo_exists(path):
        init_repo(path, repo_url)
    else:
        _ensure_remote(Path(path).resolve(), repo_url)

def create_and_push_project(path: str, project_name: str, message: str) -> None:
    base = Path(path).resolve()
    repo_path = base if base.name == project_name else base / project_name
    
    username = os.getenv("GITHUB_USERNAME", "Mekonnen44")
    ssh_alias = os.getenv("GITHUB_SSH_ALIAS", "github.com")
    
    # Construct SSH URL: git@alias:username/repo.git
    repo_url = f"git@{ssh_alias}:{username}/{project_name}.git"
    
    init_or_validate_repo(str(repo_path), repo_url)
    commit_changes(str(repo_path), message)
    push_changes(str(repo_path))