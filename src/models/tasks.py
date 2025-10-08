from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import JSON, func, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, declarative_base

Base = declarative_base()


class TaskStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    input_image_id: Mapped[int] = mapped_column(nullable=False)
    output_image_id: Mapped[Optional[int]]
    operation_type: Mapped[str]
    parameters: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(server_default=TaskStatus.QUEUED.value)
    duration_ms: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class TaskCreateDTO(BaseModel):
    input_image_id: int = Field()
    operation_type: str = Field()
    parameters: dict = Field()


class TaskDTO(TaskCreateDTO):
    id: int = Field()
    output_image_id: Optional[int] = Field()
    status: str = Field()
    duration_ms: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()

    model_config = ConfigDict(from_attributes=True)
