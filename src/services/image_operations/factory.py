from src.services.image_operations.base import Operation


class OperationFactory:
    @staticmethod
    def get_operation_cls(operation_type: str) -> type[Operation]:
        from src.services.image_operations import Reprojection, Resizing

        operations = {
            "resizing": Resizing,
            "reprojection": Reprojection,
        }
        return operations.get(operation_type)
