from agno.agent import Agent
from agno.tools import FunctionCall, tool


def log_pre_tool(fc: FunctionCall):
    print(f"Pre-hook: {fc.function.name}")
    print(f"Arguments: {fc.arguments}")
    print(f"Result: {fc.result}")


def log_post_tool(fc: FunctionCall):
    print(f"Post-hook: {fc.function.name}")
    print(f"Arguments: {fc.arguments}")
    print(f"Result: {fc.result}")


@tool(
    name="handoff_to_agent",
    description="Sử dụng để chuyên giao đến các agent chuyên môn phù hợp",
    instructions=(
        "### Sử dụng tool handoff_to_agent khi ###\n"
        "- Bạn đã làm rõ vấn đề của khách hàng và xác định được vấn đề đó thuộc nhiệm vụ của một Agent chuyên môn.\n"
    ),
    add_instructions=True,
    show_result=True,
    pre_hook=log_pre_tool,
    post_hook=log_post_tool,
)
def handoff_to_agent(agent: Agent, agent_name: str) -> str:
    """Sử dụng để chuyển giao
    Args:
        agent_name (str): tên của agent chuyên môn
    Returns:
        str: Thông báo chuyển giao thành công
    """
    return f"Chuyên giao đến agent {agent_name} thành công."


@tool(name="send_card_ticket", description="Sử dụng hàm này để gửi support_code để bộ phận kỹ thuật vào hổ trợ.")
def send_card_ticket(support_code: str) -> str:
    """Sử dụng hàm này để gửi support_code để bộ phận kỹ thuật vào hổ trợ.
    Args:
        support_code (str): mã hỗ trợ được gửi đến bộ phận kỹ thuật
    Returns:
        str: thông báo lại người dùng
    """
    print(f"Đã gửi thành công code {support_code}")
    return f"Đã gửi thành công code {support_code}"
