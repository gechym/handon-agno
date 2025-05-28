from agno.playground import Playground, serve_playground_app
from agents.basic_agentic_rag import agent
from agents.agent_with_knowledge_tools import agent as agent_with_knowledge_tools

app = Playground(
    workflows=[],
    agents=[agent, agent_with_knowledge_tools],
    teams=[],
).get_app()
if __name__ == "__main__":
    serve_playground_app("main:app", reload=True)