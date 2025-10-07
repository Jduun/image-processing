from typing import Optional

from pydantic import BaseModel, Field


class ResizingParams(BaseModel):
    width: Optional[int] = Field()
    height: Optional[int] = Field()
    resample_alg: str = Field(default="bilinear")


class ReprojectionParams(BaseModel):
    dst_srs: str = Field(default="EPSG:4326")
