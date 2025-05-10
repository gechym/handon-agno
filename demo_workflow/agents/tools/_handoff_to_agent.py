from agno.agent import Agent
from agno.tools import tool


@tool(name="handoff_to_agent", description="Xử dụng hàm này để chuyên giao đến các agent phù hợp")
def handoff_to_agent(agent: Agent, agent_id: str) -> str:
    agent.session_state['current_agent'] = agent_id
    return f"Chuyên giao đến agent {agent_id}"
