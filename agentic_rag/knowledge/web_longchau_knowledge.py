from agno.knowledge.url import UrlKnowledge

from agentic_rag.database.vector_db import vector_db

web_longchau_knowledge = UrlKnowledge(
    # urls=[
    #     "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/dinh-duong",
    #     "https://tiemchunglongchau.com.vn/",
    # ],
    vector_db=vector_db,
)

# web_longchau_knowledge.load(recreate=True)
