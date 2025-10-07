from abc import ABC, abstractmethod

from src.services.image_operations.operation import Operation


class OperationFactory(ABC):
    @classmethod
    @abstractmethod
    def create_operation(cls, operation_type: str) -> type[Operation]:
        pass
