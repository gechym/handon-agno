from agno.tools.knowledge import KnowledgeTools
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType

agno_docs = UrlKnowledge(
    urls=[
        "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/dinh-duong",
        "https://tiemchunglongchau.com.vn/",
    ],

    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

knowledge_tools = KnowledgeTools(
    knowledge=agno_docs,
    think=True,
    search=True,
    analyze=True,
    add_few_shot=True,
)

agent = Agent(
    model=OpenAIChat(id="gpt-o3-mini"),
    tools=[knowledge_tools],
    show_tool_calls=True,
    markdown=True,
)
agno_docs.load(recreate=False)
