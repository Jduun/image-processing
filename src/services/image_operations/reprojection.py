import os

from osgeo import gdal
from pydantic import ValidationError

from src.models import ReprojectionParams
from src.services.image_operations import Operation, DefaultOperationFactory


class Reprojection(Operation):
    def process(self, input_filepath: str, params: dict) -> str:
        try:
            params = ReprojectionParams.model_validate(params)
        except ValidationError as e:
            self._logger.error(
                "Ошибка валидации параметров для модели ReprojectionParams",
                exc_info=True,
                extra={"params": params, "e": e},
            )

        filepath, ext = os.path.splitext(input_filepath)
        output_filepath = f"{filepath}_reprojected{ext}"

        self._logger.info(
            "Обработка изображения: перепроецирование",
            extra={
                "input_filepath": input_filepath,
                "params": params,
            },
        )
        gdal.Warp(
            destNameOrDestDS=output_filepath,
            srcDSOrSrcDSTab=input_filepath,
            dstSRS=params.dst_srs,
        )

        return output_filepath


DefaultOperationFactory.register_operation("reprojection", Reprojection)
