from agno.storage.mongodb import MongoDbStorage

from agentic_rag.config import settings

storage_mongodb = MongoDbStorage(
    collection_name="agent",
    db_url=settings.DB_URL,
)


__all__ = ["storage_mongodb"]
