
from agno.memory.memory import Memory
from agno.storage.mongodb import MongoDbStorage


class _Setting:
    # Storage config
    agent_storage_db: MongoDbStorage = None
    workflow_storage_db: MongoDbStorage = None

    # Memory config
    agent_memory_db: Memory = None


def setup(agent_collection: str, workflow_collection: str, db_url: str, db_name: str) -> None:

    if not all([agent_collection, workflow_collection, db_url, db_name]):
        raise ValueError("Configuration parameters cannot be empty.")

    _Setting.agent_storage_db = MongoDbStorage(collection_name=agent_collection, db_url=db_url, db_name=db_name)
    _Setting.workflow_storage_db = MongoDbStorage(collection_name=workflow_collection, db_url=db_url, db_name=db_name)


def get_agent_storage_db() -> MongoDbStorage:
    # if not _Setting.agent_storage_db:
    #     raise ValueError("Agent storage database is not initialized.")
    return _Setting.agent_storage_db


def get_workflow_storage_db() -> MongoDbStorage:
    # if not _Setting.workflow_storage_db:
    #     raise ValueError("Workflow storage database is not initialized.")
    return _Setting.workflow_storage_db
