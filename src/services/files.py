import json
from http import HTTPStatus
from typing import Optional

import requests

from src.base.module import get_logger
from src.config import config
from src.models import FileDTO


class FileService:
    def __init__(self):
        self._logger = get_logger()

    @property
    def base_url(self):
        return (
            f"http://{config.file_storage.host}:"
            f"{config.file_storage.port}/api/files"
        )

    def get(self, file_id: int) -> Optional[FileDTO]:
        get_url = f"{self.base_url}/{file_id}"
        response = requests.get(get_url)

        if response.status_code != HTTPStatus.OK:
            self._logger.warning(
                "Ошибка при получении информации о файле",
                extra={
                    "id": file_id,
                    "response.text": response.text,
                },
            )
            return None

        file = FileDTO.model_validate(response.json())
        self._logger.debug("Файл найден", extra={"file": file})
        return file

    def download(self, file_id: int, filepath: str):
        download_url = f"{self.base_url}/{file_id}/download"
        response = requests.get(download_url)

        with open(filepath, "wb") as f:
            f.write(response.content)
        self._logger.info("Файл сохранен", extra={"path": filepath})

    def upload(
        self, src_filepath: str, dst_filepath: str, filename: str, comment: str
    ) -> Optional[FileDTO]:
        with open(src_filepath, "rb") as f:
            files = {"file": (filename, f)}
            data = {
                "json": json.dumps(
                    {
                        "filepath": dst_filepath,
                        "comment": comment,
                    },
                    ensure_ascii=False,
                )
            }

            upload_url = self.base_url
            response = requests.post(upload_url, files=files, data=data)

            if response.status_code != HTTPStatus.OK:
                self._logger.warning(
                    "Ошибка при загрузке файла",
                    extra={"response.text": response.text},
                )
                return None

            file = FileDTO.model_validate(response.json())

            self._logger.info(
                "Изображение сохранено в file-storage",
                extra={"filepath": file.filepath, "filename": filename},
            )

            return file
