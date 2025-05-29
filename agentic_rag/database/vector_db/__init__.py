from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType

vector_db = LanceDb(
    uri="tmp/lancedb",
    table_name="agno_docs",
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
)
