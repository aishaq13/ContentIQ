from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ContentIQ"
    environment: str = "dev"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "metadata-events"
    blob_root_path: str = "./data/blob"
    api_version: str = Field(default="v1")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CONTENTIQ_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
