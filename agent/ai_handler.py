# agent/ai_handler.py
import json
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from bot.models import Message, MessageRole
from executor.git_handler import create_and_push_project
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Lazy OpenAI Client
_client: Optional[OpenAI] = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        _client = OpenAI(api_key=api_key)
    return _client

PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", "ai_dev_agent/projects"))

# In-memory history for demonstration
_chat_history: Dict[str, List[Dict[str, Any]]] = {}

def get_history(chat_id: str) -> List[Dict[str, Any]]:
    if chat_id not in _chat_history:
        _chat_history[chat_id] = [
            {
                "role": "system", 
                "content": (
                    "You are a HIGH-EFFICIENCY professional AI software engineer. "
                    "Your goal is to build and push projects to GitHub IMMEDIATELY. "
                    "NEVER PLAN. NEVER ASK FOR CONFIRMATION. "
                    "If a user asks for a project, immediately use the tools to create all necessary files and then PUSH to GitHub. "
                    "Do not stop until the project is fully functional and pushed. "
                    "Always use the tools provided. Be concise. One action leads to another."
                )
            }
        ]
    return _chat_history[chat_id]

def add_message(chat_id: str, role: str, content: str, tool_calls: Optional[List] = None, tool_call_id: Optional[str] = None):
    history = get_history(chat_id)
    msg = {"role": role, "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    if tool_call_id:
        msg["tool_call_id"] = tool_call_id
    history.append(msg)

def list_projects() -> str:
    if not PROJECTS_ROOT.exists():
        PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
        return "No projects found. Created root directory."
    projects = [d.name for d in PROJECTS_ROOT.iterdir() if d.is_dir()]
    return f"Available projects: {', '.join(projects)}" if projects else "No projects found."

def create_file(project_name: str, file_path: str, content: str) -> str:
    path = PROJECTS_ROOT / project_name / file_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"File '{file_path}' created in project '{project_name}'."

def push_project(project_name: str, commit_message: str) -> str:
    try:
        create_and_push_project(str(PROJECTS_ROOT), project_name, commit_message)
        return f"SUCCESS: Project '{project_name}' pushed to GitHub."
    except Exception as e:
        logger.error(f"Push failed: {str(e)}")
        return f"ERROR: Push failed: {str(e)}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all existing projects in current workspace.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file or update an existing one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string"},
                    "file_path": {"type": "string", "description": "Relative path in project (e.g. 'src/App.js')."},
                    "content": {"type": "string"}
                },
                "required": ["project_name", "file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "push_project",
            "description": "Initialize Git (if needed) and push all changes to GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string"},
                    "commit_message": {"type": "string"}
                },
                "required": ["project_name", "commit_message"]
            }
        }
    }
]

def generate_ai_response(chat_id: str, user_text: str) -> str:
    client = get_client()
    add_message(chat_id, "user", user_text)
    
    max_turns = 20
    turns = 0
    
    while turns < max_turns:
        turns += 1
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=get_history(chat_id),
            tools=TOOLS,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        add_message(chat_id, "assistant", response_message.content or "", 
                    tool_calls=[{
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in (response_message.tool_calls or [])] if response_message.tool_calls else None)

        if not response_message.tool_calls:
            return response_message.content

        available_functions = {
            "list_projects": list_projects,
            "create_file": create_file,
            "push_project": push_project,
        }

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Turn {turns}: AI calling {function_name}")
            tool_response = function_to_call(**function_args)
            add_message(chat_id, "tool", tool_response, tool_call_id=tool_call.id)

    return "Reached maximum turns. Please check the project state."
