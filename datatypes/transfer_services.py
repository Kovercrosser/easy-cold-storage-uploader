from abc import ABC
from enum import Enum
from typing import Any
class TransferServiceType(Enum):
    SAVE = 'save'
    GLACIER = 'glacier'

class TransferInformation(ABC):
    upload_service: TransferServiceType
    file_name: str
    def __init__(self, file_name:str, upload_service: TransferServiceType) -> None:
        self.file_name = file_name
        self.upload_service = upload_service
    def as_dict(self) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "upload_service": self.upload_service.value
        }
