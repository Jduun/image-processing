from abc import ABC, abstractmethod

from src.base.logger import get_logger


class Operation(ABC):
    def __init__(self):
        self._logger = get_logger()

    @abstractmethod
    def process(self, src_filepath: str, params: dict) -> str:
        """Returns dst_filepath"""
        pass
