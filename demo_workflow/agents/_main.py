from agno.agent import Agent

from ._manager_agent import create_manager_agent
from ._master_banned_account_support_agent import create_master_banned_account_support_agent


class _Setting:
    manager_agent: Agent = None
    master_banned_account_support_agent: Agent = None

# def setup(base_url: str, api_key: str, model_name: str, user_id: str, session_id: str) -> None:

#     if not all([base_url, api_key, model_name, user_id, session_id]):
#         raise ValueError("Configuration parameters cannot be empty.")

#     client = openai.Client(
#         base_url=base_url,
#         api_key=api_key
#     )
#     _Setting.manager_agent = create_manager_agent(client, model_name, session_id, user_id)
#     _Setting.master_banned_account_support_agent = create_master_banned_account_support_agent(client, model_name, session_id, user_id)


def setup(base_url: str, api_key: str, model_name: str) -> None:

    if not all([base_url, api_key, model_name]):
        raise ValueError("Configuration parameters cannot be empty.")

    client = None
    # client = openai.Client(
    #     base_url=base_url,
    #     api_key=api_key
    # )
    _Setting.manager_agent = create_manager_agent(model_name, client)
    _Setting.master_banned_account_support_agent = create_master_banned_account_support_agent(model_name, client)


def get_manager_agent() -> Agent:
    return _Setting.manager_agent


def get_master_banned_account_support_agent() -> Agent:
    return _Setting.master_banned_account_support_agent
