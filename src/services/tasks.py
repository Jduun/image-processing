from http import HTTPStatus
from typing import Optional

import pika
from sqlalchemy.orm import Session

from src.base.module import get_logger, ModuleException
from src.base.sync.service import RabbitService
from src.models import Task, TaskCreateDTO, TaskDTO


class TaskService:
    def __init__(
        self,
        pg_connection: Session,
        rabbit: RabbitService,
    ):
        self._pg = pg_connection
        self._rabbit = rabbit
        self._logger = get_logger()

    def create(self, data: TaskCreateDTO) -> TaskDTO:
        self._logger.info(
            "Создание задачи",
            extra=data.model_dump(),
        )
        task = Task(**data.model_dump())
        with self._pg.begin():
            self._pg.add(task)
        self._logger.info(
            "Задача добавлена в БД",
            extra={"id": task.id},
        )
        published = self._rabbit.publish(
            {"id": task.id},
            properties=pika.BasicProperties(priority=5),
        )
        if published:
            return TaskDTO.model_validate(task)
        raise ModuleException("Не удалось добавить задачу в очередь")

    def get(self, task_id: int) -> TaskDTO:
        self._logger.info(
            "Получение задачи из БД",
            extra={"id": task_id},
        )
        with self._pg.begin():
            task: Optional[Task] = self._pg.get(Task, task_id)
            if task:
                task_dto = TaskDTO.model_validate(task)
                self._logger.info(
                    "Задача найдена",
                    extra=task_dto.model_dump(),
                )
                return task_dto
            self._logger.warning("Задача не найдена", extra={"id": task_id})
            raise ModuleException(
                "Задача не найдена", code=HTTPStatus.NOT_FOUND
            )
