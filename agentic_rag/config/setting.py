from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Settings for the agent.
    """

    _env_file: str = ".env"
    _env_file_encoding: str = "utf-8"

    def __init__(self, _env_file: str = ".env", _env_file_encoding: str = "utf-8"):
        super().__init__(_env_file=_env_file, _env_file_encoding=_env_file_encoding)

    DB_URL: str = Field(..., description="The URL of the database.")
    GOOGLE_API_KEY: str = Field(...,
                                description="The API key for the Google API.")
    OPENAI_API_KEY: str = Field(...,
                                description="The API key for the OpenAI API.")

    class Config:
        """
        Config for the settings.
        """

        extra = "ignore"


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
