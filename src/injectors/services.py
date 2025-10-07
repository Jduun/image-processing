from src.config import config
from src.injectors.connections import get_pg_session
from src.services import TaskService, RabbitService, TaskWorker, FileService


def task_service() -> TaskService:
    return TaskService(
        pg_connection=get_pg_session(),
        rabbit=rabbit(),
    )


def rabbit() -> RabbitService:
    return RabbitService(config.rabbit)


def tasks_worker() -> TaskWorker:
    return TaskWorker(
        pg_connection=get_pg_session(),
        rabbit=rabbit(),
        file_service=file_service(),
    )


def file_service() -> FileService:
    return FileService()
