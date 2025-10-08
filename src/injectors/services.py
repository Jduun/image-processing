from src.config import config
from src.injectors.connections import get_pg_session
from src.services import TaskService, RabbitService, TaskWorker, FileService
from src.services.image_operations import (
    OperationService,
    Resizing,
    Reprojection,
)


def task_service() -> TaskService:
    return TaskService(
        pg_connection=get_pg_session(),
        rabbit=rabbit(),
    )


def rabbit() -> RabbitService:
    return RabbitService(config=config.rabbit)


def file_service() -> FileService:
    return FileService(config=config.file_storage)


def operation_service() -> OperationService:
    return OperationService(
        [
            Resizing(),
            Reprojection(),
        ]
    )


def tasks_worker() -> TaskWorker:
    return TaskWorker(
        pg_connection=get_pg_session(),
        rabbit=rabbit(),
        file_service=file_service(),
        operation_service=operation_service(),
        config=config.image_processing,
    )
