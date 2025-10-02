import json
import os
import time
from http import HTTPStatus
from typing import Optional

import requests
from sqlalchemy.orm import Session

from src.config import config
from src.logger import get_logger
from src.models import Task, TaskDTO, TaskStatus
from src.rabbit import RabbitService
from src.services.image_operations import OperationFactory


class TaskWorker:
    def __init__(
        self,
        pg_connection: Session,
        rabbit: RabbitService,
    ):
        self._pg = pg_connection
        self._rabbit = rabbit
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

        with self._pg.begin():
            task_dto = TaskDTO.model_validate(task)
            self._logger.info(
                "Получена задача", extra={"task": task_dto.model_dump()}
            )
        file_storage_host = os.getenv("FILE_STORAGE_HOST")
        file_storage_port = os.getenv("FILE_STORAGE_PORT")

        base_url = f"http://{file_storage_host}:{file_storage_port}/api/files/"
        download_url = f"{base_url}{task.input_image_id}/download"
        get_url = f"{base_url}{task.input_image_id}"

        response = requests.get(get_url)
        if response.status_code != HTTPStatus.OK:
            self._logger.warning(
                "Ошибка при получении информации о файле",
                extra={
                    "id": task.input_image_id,
                    "response.text": response.text,
                },
            )
            return
        response_json = response.json()
        filepath = response_json.get("filepath")
        extension = response_json.get("extension")
        self._logger.debug(
            "", extra={"filepath": filepath, "extension": extension}
        )

        input_filepath = (
            f"{config.images_folder}/{task.input_image_id}{extension}"
        )
        os.makedirs(config.images_folder, exist_ok=True)

        try:
            response = requests.get(download_url)
            with open(input_filepath, "wb") as f:
                f.write(response.content)
        except Exception as e:
            self._update_status(task.id, TaskStatus.FAILED)
            self._logger.error(
                "Ошибка при скачивании файла", extra={"e": e}, exc_info=True
            )
            return
        self._logger.info("Файл сохранен", extra={"path": input_filepath})

        try:
            operation_cls = OperationFactory.get_operation_cls(
                task.operation_type
            )
            self._logger.info(
                "Началась обработка изображения",
                extra={
                    "input_filepath": input_filepath,
                    "parameters": task.parameters,
                },
            )
            start_time = time.perf_counter()
            output_filepath = operation_cls().process(
                input_filepath, task.parameters
            )
            end_time = time.perf_counter()
            duration_ms = int((end_time - start_time) * 1000)
            with self._pg.begin():
                self._pg.query(Task).filter(Task.id == task_id).update(
                    {"duration_ms": duration_ms}
                )
        except Exception as e:
            self._update_status(task.id, TaskStatus.FAILED)
            self._logger.error(
                "Ошибка при обработке изображения GDAL",
                extra={"e": e},
                exc_info=True,
            )
            return

        self._logger.info(
            "Изображение обработано и сохранено в image-processing",
            extra={"output_filepath": output_filepath},
        )
        upload_url = base_url
        with open(output_filepath, "rb") as f:
            filename = f"{task_id}_{os.path.basename(output_filepath)}"
            extension = os.path.splitext(output_filepath)[1]
            self._logger.debug(
                "", extra={"filename": filename, "ext": extension}
            )
            files = {"file": (filename, f)}
            data = {
                "json": json.dumps(
                    {
                        "filepath": filepath,
                        "comment": f"Обработанное изображение, задача {task.id}",
                    },
                    ensure_ascii=False,
                )
            }
            self._logger.debug(
                "Запрос в file-storage на сохранение",
                extra={"filepath": filepath, "filename": filename},
            )
            response = requests.post(upload_url, files=files, data=data)
            if response.status_code != HTTPStatus.OK:
                self._logger.warning(
                    "Ошибка при загрузке файла файле",
                    extra={"response.text": response.text},
                )
                return
            response_json = response.json()
            with self._pg.begin():
                task.output_image_id = response_json.get("id")
            self._logger.info(
                "Изображение сохранено в file-storage",
                extra={"filepath": filepath, "filename": filename},
            )
        self._update_status(task.id, TaskStatus.DONE)

    def run(self):
        self._rabbit.run_consume(self._handle_message)
