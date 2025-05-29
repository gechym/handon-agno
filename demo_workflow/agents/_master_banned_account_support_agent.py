import os
import openai

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.models.openai import OpenAIChat

from demo_workflow.tools import handoff_to_agent, send_card_ticket
from demo_workflow.database import get_agent_storage_db

def create_master_banned_account_support_agent(
    model_name: str, 
    client: openai.Client = None, 
) -> Agent:
    
    model = OpenAIChat(id=model_name, temperature=0.1) if not client else LiteLLM(
        id=model_name,
        client=client,
        temperature=0.1,
    )

    ban_account = Agent(
        name="master_banned_account_support_agent",
        agent_id="master_banned_account_support_agent",
        model=model,
        # setup database
        storage=get_agent_storage_db(),
        add_history_to_messages=True,
        num_history_runs=30,
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
        "- Bạn hãy yêu cầu người dùng cung cấp thông tin về uid hoặc tài khoản của họ.",
        "- Sau khi khách hàng cung cấp thông tin, **bắt buộc** sử dụng **tool** `send_card_ticket` với `support_code=4399` tương ứng để yêu cầu bộ phận kỹ thuật hỗ trợ và kết thúc hỗ trợ.",
        "#### **Handoff Rules:** : sử dụng handoff_to_agent để tiến hành handoff",
        "Tất cả yêu cầu khách hàng không thuộc vấn đề tài khoản bị khóa, phong cấm, hoặc không đăng nhập được hãy chuyển tiếp đến `manager_agent`",
    ]
    return agent
