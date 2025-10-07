from src.services.image_operations.abc_factory import OperationFactory
from src.services.image_operations.operation import Operation


class DefaultOperationFactory(OperationFactory):
    _operations: dict[str, type[Operation]] = {}

    @classmethod
    def register_operation(cls, name: str, operation_cls: type[Operation]):
        cls._operations[name] = operation_cls

    @classmethod
    def create_operation(cls, name: str) -> Operation:
        operation_cls = cls._operations.get(name)
        if operation_cls is None:
            raise ValueError(f"Неизвестная операция: {name}")
        return operation_cls()
