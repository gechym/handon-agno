import os
from pathlib import Path

import openai
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.litellm import LiteLLM
from dotenv import load_dotenv

load_dotenv()
dotenv_path = Path("/home/tran-tien/Documents/PyCharmProject/Work/FTech/Agno/research/.env")
load_dotenv(dotenv_path=dotenv_path)

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["LITELLM_API_KEY"] = os.getenv("LITELLM_API_KEY")

client = openai.Client(
    base_url="https://litellm.dev.ftech.ai",
    api_key=os.environ["LITELLM_API_KEY"],
)

reasoning_model = Agent(
    model=LiteLLM(
        id="vplay-va-gpt-4o-2024-11-20",
        client=client,
    ),
    reasoning_model=Gemini(
        id="gemini-2.5-flash-preview-05-20", temperature=0.6, top_p=0.95
    ),
    debug_mode=True,
    # reasoning_max_steps=3
)
# reasoning_model.print_response("9.11 and 9.9 -- which is bigger?")
reasoning_model.print_response("9.11 và 9.9 -- cái nào lớn hơn?", show_full_reasoning=True)
