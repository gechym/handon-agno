from builtins import str
from collections.abc import Iterator
from typing import cast


from agno.agent import RunResponse
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

from agentic_rag import agentic_rag
from demo_workflow._setting import setup
from demo_workflow.agents import coor_noreason_team_leader, get_manager_agent, get_master_banned_account_support_agent
from demo_workflow.agents import coor_reason_team_leader as coor_reason_team_leader
from demo_workflow.database import get_agent_storage_db as get_agent_storage_db
from demo_workflow.database import get_workflow_storage_db

from rich.pretty import pprint

setup("config/config.yaml")

agents = {
    "master_banned_account_support_agent": get_master_banned_account_support_agent(),
    "manager_agent": get_manager_agent(),
    "agentic_rag": agentic_rag,
    "team_leader": coor_noreason_team_leader,  # coor_reason_team_leader
}


class SimpleWorkflow(Workflow):
    description: str = "A simple workflow"
    manager_agent = get_manager_agent()
    banned_account_support_agent = get_master_banned_account_support_agent()

    def run(self, message: str, user_id: str = "gechym", session_id: str = "demo") -> Iterator[RunResponse]:
        self.session_id = session_id
        self.user_id = user_id
        self.storage.mode = "agent"
        session = self.storage.read(
            session_id=session_id,
            user_id=user_id
        )
        print(f"Session: {session}")

        pre_agent = session.session_data.get("session_state", {}).get("current_agent", "manager_agent") if session else "manager_agent"

        while True:
            agent_run = agents.get(pre_agent, self.manager_agent)
            result = agent_run.run(message, session_id=session_id, user_id=user_id)

            current_agent = agent_run.session_state.get("current_agent", pre_agent)

            if current_agent == pre_agent:
                return cast(RunResponse, result)

            pre_agent = current_agent
            self.session_state["current_agent"] = current_agent


workflow = SimpleWorkflow(
    storage=get_workflow_storage_db()
)

if __name__ == "__main__":
    while True:
        message = input("Enter message: ")
        if message.lower() == "exit":
            break
        report = workflow.run(message=message)
        try:
            pprint_run_response(report, markdown=True, show_time=True)
        except Exception as e:
            pass