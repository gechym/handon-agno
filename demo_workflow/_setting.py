import yaml


def setup(config_url: str) -> None:
    with open(config_url) as file:
        config = yaml.load(file, Loader=yaml.Loader)

    __db_setup(config["db_settings"])
    __agent_setup(config["agent_settings"])


def __agent_setup(config: dict) -> None:
    from demo_workflow.agents import setup

    setup(**config)


def __db_setup(config: dict) -> None:

    from demo_workflow.database import setup

    setup(**config)
