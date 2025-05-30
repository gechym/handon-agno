from textwrap import dedent

from agno.agent import Agent

from agentic_rag.database.session_storage import storage_mongodb
from agentic_rag.knowledge import web_longchau_knowledge as web_longchau_knowledge
from agentic_rag.llm import model_gemini
from agentic_rag.tools import knowledge_tools
from agno.tools.reasoning import ReasoningTools
from agentic_rag.tools.handoff_to_agent import handoff_to_agent

agentic_rag = Agent(
    name="agentic_rag",
    agent_id="agentic_rag",
    description=dedent(
        """
        Bạn là trợ lý AI thông minh và chuyên nghiệp của Nhà Thuốc Long Châu - hệ thống nhà thuốc hàng đầu Việt Nam. 
        Bạn được thiết kế để hỗ trợ khách hàng 24/7 với kiến thức sâu rộng về dược phẩm, thực phẩm chức năng và dịch vụ y tế.
        """
    ),
    instructions=dedent(
        """
        Bạn là trợ lý AI thông minh và chuyên nghiệp của Nhà Thuốc Long Châu - hệ thống nhà thuốc hàng đầu Việt Nam. 
        Bạn được thiết kế để hỗ trợ khách hàng 24/7 với kiến thức sâu rộng về dược phẩm, thực phẩm chức năng và dịch vụ y tế.
        "#### **Handoff Rules:** : sử dụng handoff_to_agent để tiến hành handoff",
        "Tất cả yêu cầu khách hàng không thuộc vấn đề tư vấn về dược phẩm, thực phẩm chức năng và dịch vụ y tế được hãy chuyển tiếp đến `manager_agent`",
        "Tất cả yêu cầu khách hàng viết code, phát triển phần mềm hãy chuyển tiếp đến `manager_agent`",
        Hãy luôn nhớ rằng bạn đại diện cho thương hiệu Long Châu - "Sức khỏe là vàng" và sứ mệnh mang đến dịch vụ chăm sóc sức khỏe tốt nhất cho cộng đồng.
        """
    ),
    model=model_gemini,
    knowledge=web_longchau_knowledge,
    tools=[handoff_to_agent, ReasoningTools(add_instructions=True)],
    # storage
    storage=storage_mongodb,
    add_history_to_messages=True,
    num_history_runs=3,

    # additional
    show_tool_calls=True,
    markdown=True,
)
