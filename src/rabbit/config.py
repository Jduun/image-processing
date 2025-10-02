from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class _CredentialsConfig(BaseSettings):
    host: str = Field(default="rabbit")
    port: int = Field(default=5672)
    user: str = Field(default="admin")
    password: str = Field(default="12345")


class RabbitPublisherConfig(_CredentialsConfig):
    exchange: str = Field(default="")
    routing_key: str = Field(default="")
    reply_to: Optional[str] = Field(default=None)


class RabbitConsumerConfig(_CredentialsConfig):
    queue_name: str = Field(default="")
    error_timeout: int = Field(default=10)
    max_priority: int = Field(default=5)


class RabbitFullConfig(RabbitConsumerConfig, RabbitPublisherConfig):
    pass
