from agno.playground import Playground, serve_playground_app

from agentic_rag import agentic_rag
from demo_workflow import workflow

app = Playground(workflows=[workflow], agents=[agentic_rag]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
