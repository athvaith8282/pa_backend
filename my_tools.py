from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from typing import Annotated
from my_state import Todo

from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from prompts import WRITE_TODOS_SYSTEM_PROMPT

from my_state import MyState

from langchain_core.callbacks import adispatch_custom_event

tavily_search = TavilySearch(
    max_results = 5
)

@tool(description=WRITE_TODOS_SYSTEM_PROMPT)
async def write_todos(
    todos: list[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    await adispatch_custom_event( 
        name="on_todo_update",
        data={
            "todo": todos
        }
    )
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(f"Updated todo list to {todos}", tool_call_id=tool_call_id)
            ],
        }
    )

@tool()
async def read_todos(state: Annotated[MyState, InjectedState]):
    """Read the current TODO list from the agent state.

    This tool allows the agent to retrieve and review the current TODO list
    to stay focused on remaining tasks and track progress through complex workflows.

    Args:
        state: Injected agent state containing the current TODO list
        tool_call_id: Injected tool call identifier for message tracking

    Returns:
        Formatted string representation of the current TODO list
    """

    todos = state.get("todos", [])
    if not todos:
        return "No todos currently in the list."

    result = "Current TODO List:\n"
    for i, todo in enumerate(todos, 1):
        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
        emoji = status_emoji.get(todo["status"], "❓")
        result += f"{i}. {emoji} {todo['content']} ({todo['status']})\n"

    return result.strip()

def get_tools():

    return [
        tavily_search, read_todos, write_todos
    ]