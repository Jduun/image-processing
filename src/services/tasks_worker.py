import os
import time
from typing import Optional

from sqlalchemy.orm import Session

from src.base.module import get_logger
from src.base.sync.service import RabbitService
from src.config import ImageProcessingConfig
from src.models import Task, TaskStatus
from src.services.image_operations import OperationService
from src.services.files import FileService


class TaskWorker:
    def __init__(
        self,
        pg_connection: Session,
        rabbit: RabbitService,
        file_service: FileService,
        operation_service: OperationService,
        config: ImageProcessingConfig,
    ):
        self._pg = pg_connection
        self._rabbit = rabbit
        self._file_service = file_service
        self._operation_service = operation_service
        self._config = config
        self._logger = get_logger()

    def _get_task(self, task_id: int) -> Optional[Task]:
        with self._pg.begin():
            task: Optional[Task] = self._pg.get(Task, task_id)
            if not task:
                return None

        self._update_status(task.id, TaskStatus.PROCESSING)
        return task

    def _update_status(self, task_id: int, status: TaskStatus):
        with self._pg.begin():
            self._pg.query(Task).filter(Task.id == task_id).update(
                {"status": status.value}
            )

    def _handle_message(self, message: dict, **_):
        task_id = message.get("id")
        task: Optional[Task] = self._get_task(task_id)
        if task is None:
            self._logger.warning("Задача не найдена", extra={"id": task_id})
            return

        file = self._file_service.get(task.input_image_id)
        src_filepath = f"{self._config.folder}/{file.id}{file.extension}"
        os.makedirs(self._config.folder, exist_ok=True)

        try:
            self._file_service.download(file.id, src_filepath)

            start_time = time.perf_counter()
            operation = self._operation_service.get_operation(
                task.operation_type
            )
            dst_filepath = operation.process(src_filepath, task.parameters)
            end_time = time.perf_counter()

            duration_ms = int((end_time - start_time) * 1000)
            with self._pg.begin():
                self._pg.query(Task).filter(Task.id == task_id).update(
                    {"duration_ms": duration_ms}
                )
        except Exception as e:
            self._update_status(task.id, TaskStatus.FAILED)
            self._logger.error(
                "Ошибка при обработке изображения",
                extra={"e": e},
                exc_info=True,
            )
            return

        self._logger.info(
            "Изображение обработано и сохранено в image-processing",
            extra={"dst_filepath": dst_filepath},
        )

        filename = f"{task_id}_{os.path.basename(dst_filepath)}"
        comment = f"Обработанное изображение, задача {task.id}"
        uploaded_file = self._file_service.upload(
            dst_filepath, file.filepath, filename, comment
        )
        with self._pg.begin():
            task.output_image_id = uploaded_file.id

        self._update_status(task.id, TaskStatus.DONE)

    def run(self):
        self._rabbit.run_consume(self._handle_message)
