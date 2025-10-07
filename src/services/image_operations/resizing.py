import os

from osgeo import gdal
from pydantic import ValidationError

from src.models import ResizingParams
from src.services.image_operations import Operation, DefaultOperationFactory


class Resizing(Operation):
    def process(self, src_filepath: str, params: dict) -> str:
        try:
            params = ResizingParams.model_validate(params)
        except ValidationError as e:
            self._logger.error(
                "Ошибка валидации параметров для модели ResizingParams",
                exc_info=True,
                extra={"params": params, "e": e},
            )

        dataset: gdal.Dataset = gdal.Open(src_filepath)
        width, height = dataset.RasterXSize, dataset.RasterYSize

        if params.width is None:
            params.width = width
        if params.height is None:
            params.height = height
        if params.width == width and params.height == height:
            return src_filepath

        filepath, ext = os.path.splitext(src_filepath)
        dst_filepath = f"{filepath}_resized{ext}"

        self._logger.info(
            "Обработка изображения: изменение разрешения",
            extra={
                "src_filepath": src_filepath,
                "parameters": params,
            },
        )
        gdal.Warp(
            dst_filepath,
            dataset,
            width=params.width,
            height=params.height,
            resampleAlg=params.resample_alg,
        )

        return dst_filepath


DefaultOperationFactory.register_operation("resizing", Resizing)
