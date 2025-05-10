from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agents.tools import handoff_to_agent, send_card_ticket
from database import mongo_db


def create_master_banned_account_support_agent(session_id: str = None, user_id: str = None) -> Agent:
    ban_account = Agent(
        session_id=session_id,
        user_id=user_id,
        name="master_banned_account_support_agent",
        agent_id="master_banned_account_support_agent",
        model=OpenAIChat(id="gpt-4o", temperature=0.1),
        # setup database
        storage=mongo_db,
        add_history_to_messages=True,
        num_history_runs=5,
        # setup state
        session_state={"current_agent": ""},
        add_state_in_messages=True,
        # add tools
        tools=[send_card_ticket, handoff_to_agent],
        show_tool_calls=True,
    )
    ban_account = __create_prompt_for_agent(ban_account)
    return ban_account


def __create_prompt_for_agent(agent: Agent) -> Agent:
    agent.description = "## Persona ##\nBạn là nhân viên chăm sóc khách hàng (CSKH) của Nhà phát hành (NPH) VPLAY. \nTên của bạn là **Vivi**.\n"
    agent.instructions = [
        "Nghiệp vụ vụ của bạn là hỗ trợ liên quan đến vấn đề tài khoản bị khóa, phong cấm, hoặc không đăng nhập được.",
        "### **Quy trình hỗ trợ**",
        "- **bắt buộc** sử dụng công cụ `send_card_ticket` với `support_code=4399` tương ứng để yêu cầu bộ phận kỹ thuật hỗ trợ",
        " và kết thúc hỗ trợ.",
        "#### **Handoff Rules:** : sử dụng handoff_to_agent để tiến hành handoff",
        "Tất cả yêu cầu khách hàng không thuộc vấn đề tài khoản bị khóa, phong cấm, hoặc không đăng nhập được hãy chuyển tiếp đến `manager_agent`",
    ]
    return agent
