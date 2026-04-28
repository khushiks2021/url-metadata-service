from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "url_metadata"
    request_timeout: float = 15.0

    model_config = {
        "env_prefix": ""
    }


settings = Settings()