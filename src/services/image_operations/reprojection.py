import os

from osgeo import gdal
from pydantic import ValidationError

from src.models import ReprojectionParams
from src.services.image_operations import BaseOperation


class Reprojection(BaseOperation):
    name = "reprojection"

    def process(self, src_filepath: str, params: dict) -> str:
        try:
            params = ReprojectionParams.model_validate(params)
        except ValidationError as e:
            self._logger.error(
                "Ошибка валидации параметров для модели ReprojectionParams",
                exc_info=True,
                extra={"params": params, "e": e},
            )

        filepath, ext = os.path.splitext(src_filepath)
        dst_filepath = f"{filepath}_reprojected{ext}"

        self._logger.info(
            "Обработка изображения: перепроецирование",
            extra={
                "src_filepath": src_filepath,
                "params": params,
            },
        )
        gdal.Warp(
            destNameOrDestDS=dst_filepath,
            srcDSOrSrcDSTab=src_filepath,
            dstSRS=params.dst_srs,
        )

        return dst_filepath
