from src.services.image_operations.base import BaseOperation


class OperationService:
    def __init__(self, operations: list[BaseOperation]):
        self._operations = {
            operation.name: operation for operation in operations
        }

    def get_operation(self, name: str) -> BaseOperation:
        operation = self._operations.get(name)
        if operation is None:
            raise ValueError(f"Неизвестная операция: {name}")

        return operation
