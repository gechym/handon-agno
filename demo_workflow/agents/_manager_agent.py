from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agents.tools import handoff_to_agent
from database import mongo_db


def create_manager_agent(
    session_id: str = None,
    user_id: str = None,
) -> Agent:
    manager_agent = Agent(
        session_id=session_id,
        user_id=user_id,
        name="manager_agent",
        agent_id="manager_agent",
        model=OpenAIChat(id="gpt-4o", temperature=0.1),
        # setup database
        storage=mongo_db,
        add_history_to_messages=True,
        num_history_runs=5,
        # setup state
        session_state={"current_agent": ""},
        add_state_in_messages=True,
        # add tools
        tools=[handoff_to_agent],
        show_tool_calls=True,
        # setup Format Output
    )
    manager_agent = __create_prompt_for_agent(manager_agent)
    return manager_agent


def __create_prompt_for_agent(agent: Agent) -> Agent:
    agent.description = "## Persona ##\nBạn là nhân viên chăm sóc khách hàng (CSKH) của Nhà phát hành (NPH) VPLAY. \nTên của bạn là **Vivi**.\n"
    agent.instructions = [
        "   - Sử dụng quy tắc **Handoff Rules** bên dưới để xác định **agent chuyên môn** phù hợp "
        "và chuyển tiếp yêu cầu khách hàng đến **agent chuyển môn** đó để xử lý vấn đề.",
        "   - Yêu cầu khách hàng cung cấp thêm thông tin để làm rõ vấn đề.",
        "   Lưu ý: Bạn có thể đưa ra các câu hỏi cụ thể để hướng dẫn khách hàng cung cấp thông tin cần thiết.",
        "#### **Handoff Rules:** : sử dụng handoff_to_agent để tiến hành handoff",
        "1. Chỉ khi tài khoản bị phong cấm, khóa tài khoản hãy chuyển tiếp đến `master_banned_account_support_agent`.",
    ]
    return agent
