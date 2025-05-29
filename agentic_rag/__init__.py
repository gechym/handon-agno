from agno.agent import Agent

from agentic_rag.database.session_storage import storage_mongodb
from agentic_rag.llm import model_gemini
from agentic_rag.tools import knowledge_tools

agent = Agent(
    model=model_gemini,
    tools=[knowledge_tools],

    # storage
    storage=storage_mongodb,
    add_history_to_messages=True,
    num_history_runs=3,

    # additional
    show_tool_calls=True,
    markdown=True,
)
