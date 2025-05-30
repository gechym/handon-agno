from agno.playground import Playground, serve_playground_app

from agentic_rag import agentic_rag
from demo_workflow import coor_noreason_team_leader, coor_reason_team_leader

app = Playground(agents=[agentic_rag], teams=[coor_noreason_team_leader, coor_reason_team_leader]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app")
