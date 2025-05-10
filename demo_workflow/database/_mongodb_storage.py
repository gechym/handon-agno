import os

from agno.storage.mongodb import MongoDbStorage
from agno.storage.sqlite import SqliteStorage
from dotenv import load_dotenv

load_dotenv(override=True)
mongo_db = MongoDbStorage(collection_name="sessions",db_url=os.getenv("DB_URL"), db_name=os.getenv("DB_NAME"))
mongo_db_workflow = MongoDbStorage(collection_name="workflow",db_url=os.getenv("DB_URL"), db_name=os.getenv("DB_NAME"))
