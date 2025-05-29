from agno.tools.knowledge import KnowledgeTools

from agentic_rag.knowledge import web_longchau_knowledge

knowledge_tools = KnowledgeTools(
    knowledge=web_longchau_knowledge,
    think=True,
    search=True,
    analyze=True,
    add_few_shot=True,
)
