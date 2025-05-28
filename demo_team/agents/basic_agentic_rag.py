from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.vectordb.lancedb import LanceDb, SearchType

# Load Agno documentation in a knowledge base
knowledge = UrlKnowledge(
    urls=[
        "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/dinh-duong",
        "https://tiemchunglongchau.com.vn/",
    ],
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
    ),
)
agent = Agent(
    name="Agno Assist",
    model=OpenAIChat(id="gpt-o3-mini"),
    instructions=[
        "Bạn là trợ lý ảo của nhà thuốc long châu",
        "luôn luôn tìm kiếm trong cơ sở dữ liệu của bạn để trả lời câu hỏi",
        "nếu không tìm thấy thông tin trong cơ sở dữ liệu, hãy nói rằng bạn không biết",
        "nếu có thể, hãy cung cấp đường dẫn đến trang web của bạn để người dùng có thể tìm hiểu thêm",
    ],
    knowledge=knowledge,
    tools=[ReasoningTools(add_instructions=True)],
    add_datetime_to_instructions=True,
    num_history_runs=10,
    markdown=True,
    show_tool_calls=True,
)
# agent.knowledge.load(recreate=False)
