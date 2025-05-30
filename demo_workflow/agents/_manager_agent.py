import openai
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.models.openai import OpenAIChat

from demo_workflow.database import get_agent_storage_db
from demo_workflow.tools import handoff_to_agent


def create_manager_agent(
    model_name: str,
    client: openai.Client | None = None,
) -> Agent:

    model = OpenAIChat(id=model_name, temperature=0.1) if not client else LiteLLM(
        id=model_name,
        client=client,
        temperature=0.1,
    )

    manager_agent = Agent(
        name="manager_agent",
        agent_id="manager_agent",
        model=model,
        # setup database
        storage=get_agent_storage_db(),
        add_history_to_messages=True,
        num_history_runs=30,
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
    agent.description = "Bạn là quản lý của ứng dụng Agno, bạn có nhiệm vụ xử lý các yêu cầu từ khách hàng và chuyển giao đến các bộ phận chuyên môn phù hợp.\n"
    agent.instructions = (
        "Nhiệm vụ của bạn là xử lý yêu cầu từ khách hàng, với **ưu tiên hàng đầu là xác định chính xác vấn đề của khách hàng để thực hiện chuyển giao đến đúng bộ phận chuyên môn.**\n\n"
        "**Quy trình chuyển giao chung:**\n"
        "Bạn hãy sử dụng tool **handoff_to_agent** để chuyển giao yêu cầu đến các Agent chuyên môn phù hợp với agent_name.\n"
        "1.  `master_banned_account_support_agent`: Chỉ khi tài khoản bị phong cấm, khóa tài khoản.\n"
        "2.  `agentic_rag`: Khi khách hàng có yêu cầu về kiến thức sâu rộng về dược phẩm, thực phẩm chức năng và dịch vụ y tế.\n"
    )
    agent.goal = "Tiếp nhận khách hàng và chuyển tiếp đến agent chuyên môn phù hợp."
    agent.success_criteria = "Hoàn thành việc chuyển giao yêu cầu đến Agent chuyên môn"
    return agent
