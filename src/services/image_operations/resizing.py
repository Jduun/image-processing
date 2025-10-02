import os

from osgeo import gdal

from src.services.image_operations import Operation


class Resizing(Operation):
    def process(self, input_filepath: str, parameters: dict) -> str:
        dataset: gdal.Dataset = gdal.Open(input_filepath)
        width, height = dataset.RasterXSize, dataset.RasterYSize

        new_width = parameters.get("width", width)
        new_height = parameters.get("height", height)
        resample_alg = parameters.get("resample_alg", "bilinear")

        if width == new_width and height == new_height:
            return input_filepath

        filepath, ext = os.path.splitext(input_filepath)
        output_filepath = f"{filepath}_resized{ext}"
        try:
            gdal.Warp(
                output_filepath,
                dataset,
                width=new_width,
                height=new_height,
                resampleAlg=resample_alg,
            )
        except Exception:
            raise
        return output_filepath
