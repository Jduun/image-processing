import os

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

from src.rabbit import RabbitFullConfig


class PostgresConfig(BaseSettings):
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    host: str = Field(default="file-storage-db")
    db: str = Field(default="db")


class AppConfig(BaseSettings):
    images_folder: str = Field(default="/images")
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbit: RabbitFullConfig = Field(default_factory=RabbitFullConfig)


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)


config = load_config(os.getenv("YAML_PATH"))
