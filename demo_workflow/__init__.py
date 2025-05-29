from builtins import str
from collections.abc import Iterator

from agno.agent import RunResponse
from agno.playground import Playground, serve_playground_app
from agno.workflow import Workflow
from deepdiff import grep
from sqlalchemy.sql.functions import session_user

from demo_workflow.agents import get_manager_agent, get_master_banned_account_support_agent
from demo_workflow.database import get_agent_storage_db, get_workflow_storage_db
from demo_workflow._setting import setup
from agno.utils.pprint import pprint_run_response

setup("/home/tran-tien/Documents/PyCharmProject/Work/FTech/Agno/handon-agno/config/config.yaml")

agents = {
    "master_banned_account_support_agent": get_master_banned_account_support_agent(),
    "manager_agent": get_manager_agent()
}

class SimpleWorkflow(Workflow):
    description: str = "A simple workflow"
    manager_agent = get_manager_agent()
    banned_account_support_agent = get_master_banned_account_support_agent()
    # storage = get_workflow_storage_db()

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
                return result

            pre_agent = current_agent
            self.session_state["current_agent"] = current_agent
        # if session and session.session_data.get("session_state", None):
        # pre_agent = ""
        # if session:
        #     pre_agent = session.session_data.get("session_state", {}).get("current_agent", None)
        #
        # if pre_agent:
        #     if pre_agent == "master_banned_account_support_agent":
        #         result = self.banned_account_support_agent.run(message, session_id=session_id, user_id=user_id)
        #         current_agent = self.banned_account_support_agent.session_state.get("current_agent", pre_agent)
        # else:
        #     result = self.manager_agent.run(message, session_id=session_id, user_id=user_id)
        #     current_agent = self.manager_agent.session_state.get("current_agent", None)
        #     print(result)
        #
        # if pre_agent == current_agent or not all[pre_agent, current_agent]:
        #     return result
        #
        # if current_agent == "master_banned_account_support_agent":
        #     result = self.banned_account_support_agent.run(message, session_id=session_id, user_id=user_id, stream=True)
        #
        #     return result

        # if self.session_state
        # if session and session.session_data.get("session_state", None):
        #     if session.session_data.get("session_state")["current_agent"]:
        #         current_agent = session.session_data.get("session_state")["current_agent"]
        #         if current_agent == "master_banned_account_support_agent":
        #             yield from self.banned_account_support_agent.run(message, session_id=session_id, user_id=user_id, stream=True)
        #         if current_agent == "manager_agent":
        #             yield from self.manager_agent.run(message, session_id=session_id, user_id=user_id, stream=True)
        #         session_3 = self.database_session.read(
        #             session_id=session_id,
        #             user_id=user_id
        #         )
        #         # check db session_State đã thay đổi và tiến hành gọi agent_current vào xử lý tiếp chứ ko được kết thúc một turn
        #         if session_3.agent_id != session_3.session_data.get("session_state")["current_agent"]:  # Tiếp tục agent được handoff để vào hổ trợ user
        #             if session_3.session_data.get("session_state")["current_agent"] == "master_banned_account_support_agent":
        #                 yield from self.banned_account_support_agent.run("hãy hỗ trợ user", session_id=session_id, user_id=user_id, stream=True)
        #             if session_3.session_data.get("session_state")["current_agent"] == "manager_agent":
        #                 yield from self.manager_agent.run("hãy hỗ trợ user", session_id=session_id, user_id=user_id, stream=True)
        #         return
        # yield from self.manager_agent.run(message, session_id=session_id, user_id=user_id, stream=True)

        # # check db session_State đã thay đổi và tiến hành gọi agent_current vào xử lý tiếp chứ ko được kết thúc một turn
        # session_2 = self.database_session.read(
        #     session_id=session_id,
        #     user_id=user_id
        # )
        # if session_2.session_data.get("session_state")["current_agent"] == "":  # Turn đầu
        #     return

        # # Tiếp tục agent được handoff để vào hổ trợ user
        # if session_2.agent_id != session_2.session_data.get("session_state")["current_agent"]:
        #     if session_2.session_data.get("session_state")["current_agent"] == "master_banned_account_support_agent":
        #         yield from self.banned_account_support_agent.run("hãy hổ trợ user", session_id=session_id, user_id=user_id, stream=True)
        #     if session_2.session_data.get("session_state")["current_agent"] == "manager_agent":
        #         yield from self.manager_agent.run("hãy hổ trợ user", session_id=session_id, user_id=user_id, stream=True)
        # return

workflow = SimpleWorkflow(
    storage=get_workflow_storage_db()
)

while True:
    message = input("Enter message: ")
    if message.lower() == "exit":
        break

    report = workflow.run(message=message)

    # Print the report
    pprint_run_response(report, markdown=True, show_time=True)

# workflow = SimpleWorkflow(
#     storage=mongo_db_workflow,
# )
# app = Playground(workflows=[workflow], agents=[create_manager_agent()]).get_app()
# if __name__ == "__main__":
#     serve_playground_app("main:app", reload=True)
