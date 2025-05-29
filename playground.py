from agno.playground import Playground, serve_playground_app

from agentic_rag import agent

app = Playground(agents=[agent]).get_app()


if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
