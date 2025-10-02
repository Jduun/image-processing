import abc


class Operation(abc.ABC):
    @abc.abstractmethod
    def process(self, filepath: str, parameters: dict) -> str:
        """Returns output filepath"""
        pass
