from abc import ABC, abstractmethod

from src.base.module import get_logger
from src.services.image_operations.timer import timer


class Operation(ABC):
    def __init__(self):
        self._logger = get_logger()

    @timer
    @abstractmethod
    def process(self, src_filepath: str, params: dict) -> str:
        """Returns dst_filepath"""
        pass
