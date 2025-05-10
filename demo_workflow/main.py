from collections.abc import Iterator

from agno.agent import RunResponse
from agno.playground import Playground, serve_playground_app
from agno.workflow import Workflow

from agents import create_manager_agent, create_master_banned_account_support_agent
from database import mongo_db, mongo_db_workflow


class SimpleWorkflow(Workflow):
    description: str = "A simple workflow"
    manager_agent = create_manager_agent()
    banned_account_support_agent = create_master_banned_account_support_agent()
    database_session = mongo_db

    def run(self, message: str, user_id: str = "gechym", session_id: str = "demo") -> Iterator[RunResponse]:
        self.session_id = session_id
        self.user_id = user_id
        session = self.database_session.read(
            session_id=session_id,
            user_id=user_id
        )
        if session and session.session_data.get("session_state", None):
            if session.session_data.get("session_state")["current_agent"]:
                current_agent = session.session_data.get("session_state")["current_agent"]
                if current_agent == "master_banned_account_support_agent":
                    yield from self.banned_account_support_agent.run(message, session_id=session_id, user_id=user_id, stream=True)
                if current_agent == "manager_agent":
                    yield from self.manager_agent.run(message, session_id=session_id, user_id=user_id, stream=True)
                session_3 = self.database_session.read(
                    session_id=session_id,
                    user_id=user_id
                )
                # check db session_State đã thay đổi và tiến hành gọi agent_current vào xử lý tiếp chứ ko được kết thúc một turn
                if session_3.agent_id != session_3.session_data.get("session_state")["current_agent"]:  # Tiếp tục agent được handoff để vào hổ trợ user
                    if session_3.session_data.get("session_state")["current_agent"] == "master_banned_account_support_agent":
                        yield from self.banned_account_support_agent.run("hãy hỗ trợ user", session_id=session_id, user_id=user_id, stream=True)
                    if session_3.session_data.get("session_state")["current_agent"] == "manager_agent":
                        yield from self.manager_agent.run("hãy hỗ trợ user", session_id=session_id, user_id=user_id, stream=True)
                return
        yield from self.manager_agent.run(message, session_id=session_id, user_id=user_id, stream=True)

        # check db session_State đã thay đổi và tiến hành gọi agent_current vào xử lý tiếp chứ ko được kết thúc một turn
        session_2 = self.database_session.read(
            session_id=session_id,
            user_id=user_id
        )
        if session_2.session_data.get("session_state")["current_agent"] == "":  # Turn đầu
            return

        # Tiếp tục agent được handoff để vào hổ trợ user
        if session_2.agent_id != session_2.session_data.get("session_state")["current_agent"]:
            if session_2.session_data.get("session_state")["current_agent"] == "master_banned_account_support_agent":
                yield from self.banned_account_support_agent.run("hãy hổ trợ user", session_id=session_id, user_id=user_id, stream=True)
            if session_2.session_data.get("session_state")["current_agent"] == "manager_agent":
                yield from self.manager_agent.run("hãy hổ trợ user", session_id=session_id, user_id=user_id, stream=True)
        return


workflow = SimpleWorkflow(
    storage=mongo_db_workflow,
)
app = Playground(workflows=[workflow], agents=[create_manager_agent()]).get_app()
if __name__ == "__main__":
    serve_playground_app("main:app", reload=True)
