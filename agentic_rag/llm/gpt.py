from agentic_rag.config import settings
from agno.models.openai import OpenAIChat

model_gpt = OpenAIChat(id="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
