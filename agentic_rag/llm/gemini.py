from agno.models.google import Gemini

from agentic_rag.config import settings

model_gemini = Gemini(id="gemini-2.0-flash", api_key=settings.GOOGLE_API_KEY)
