

from typing import Any


class Service:
    def __init__(self) -> None:
        self.compression_service = None
        self.encryption_service = None
        self.filetype_service = None
        self.transfer_service = None
        self.rich_console = None
        self.cancel_service = None

    def set_service(self, service_ref: Any, service_name: str) -> None:
        if service_ref is None:
            raise ValueError("Service reference cannot be None.")
        setattr(self, service_name, service_ref)

    def get_service(self, service_name: str) -> Any:
        val = getattr(self, service_name)
        if val is None:
            raise ValueError(f"Service {service_name} not set.")
        return val
