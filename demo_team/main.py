from agents.team_collaborate import agent_team
from agents.team_coordinate import editor
from agents.team_router import multi_language_team
from agents.workflow_team import TeamWorkflow
from agno.playground import Playground, serve_playground_app

app = Playground(workflows=[TeamWorkflow()], agents=[], teams=[multi_language_team, editor, agent_team]).get_app()
if __name__ == "__main__":
    serve_playground_app("main:app", reload=True)
