import os

from osgeo import gdal

from src.services.image_operations import Operation


class Reprojection(Operation):
    def process(self, input_filepath: str, parameters: dict) -> str:
        filepath, ext = os.path.splitext(input_filepath)
        output_filepath = f"{filepath}_reprojected{ext}"
        dst_srs = parameters.get("dst_srs", "EPSG:4326")

        try:
            gdal.Warp(
                destNameOrDestDS=output_filepath,
                srcDSOrSrcDSTab=input_filepath,
                dstSRS=dst_srs,
            )
        except Exception:
            raise

        return output_filepath
