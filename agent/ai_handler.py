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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", "ai_dev_agent/projects"))

# In-memory history for demonstration (Stateful per chat_id)
# Note: For Render workers, this will be lost on restart unless using a DB.
_chat_history: Dict[str, List[Dict[str, Any]]] = {}

def get_history(chat_id: str) -> List[Dict[str, Any]]:
    if chat_id not in _chat_history:
        _chat_history[chat_id] = [
            {"role": "system", "content": "You are a professional AI software engineer. You help users build projects and push them to GitHub. Use the provided tools to manage files and git operations. Be concise and professional."}
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
    return f"File '{file_path}' created/updated in project '{project_name}'."

def push_project(project_name: str, commit_message: str) -> str:
    try:
        # Assuming the projects root is ai_dev_agent/projects as per .env
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
            "description": "List all existing projects currently in the developer workspace.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file or overwrite an existing one with new content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Name of the project folder."},
                    "file_path": {"type": "string", "description": "Relative path within the project (e.g. 'src/main.py')."},
                    "content": {"type": "string", "description": "Full content of the file."}
                },
                "required": ["project_name", "file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "push_project",
            "description": "Initialize/Validate Git repository and push all changes to GitHub.",
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
    # 1. Add User message to history
    add_message(chat_id, "user", user_text)
    
    # 2. Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=get_history(chat_id),
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 3. Handle Tool Calls
    if tool_calls:
        # Add Assistant message with tool_calls to history
        # Convert tool_calls objects to dictionaries for storage
        tool_calls_dict = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in tool_calls
        ]
        add_message(chat_id, "assistant", response_message.content or "", tool_calls=tool_calls_dict)

        available_functions = {
            "list_projects": list_projects,
            "create_file": create_file,
            "push_project": push_project,
        }

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"AI calling tool: {function_name} with {function_args}")
            tool_response = function_to_call(**function_args)
            
            # Add Tool result to history
            add_message(chat_id, "tool", tool_response, tool_call_id=tool_call.id)

        # 4. Generate final response after tool execution
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=get_history(chat_id)
        )
        assistant_final_text = final_response.choices[0].message.content
        add_message(chat_id, "assistant", assistant_final_text)
        return assistant_final_text

    # No tool calls, just normal response
    add_message(chat_id, "assistant", response_message.content)
    return response_message.content
