import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

from src.base.sync.models import RabbitFullConfig


class PostgresConfig(BaseSettings):
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    host: str = Field(default="file-storage-db")
    db: str = Field(default="db")


class FileStorageConfig(BaseSettings):
    host: str = Field(default="file-storage")
    port: int = Field(default=80)


class ImageProcessingConfig(BaseSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=80)
    folder: str = Field(default="/images")
    debug: bool = Field(default=False)


class AppConfig(BaseSettings):
    image_processing: ImageProcessingConfig = Field(
        default_factory=ImageProcessingConfig
    )
    file_storage: FileStorageConfig = Field(default_factory=FileStorageConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbit: RabbitFullConfig = Field(default_factory=RabbitFullConfig)


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)


config = load_config("/app/src/config/config.yaml")
