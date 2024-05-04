from abc import ABC, abstractmethod
from typing import Any, Generator

from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from utils.report_utils import ReportManager

class TransferBase(ABC):

    @staticmethod
    def get_file_extension(service: Service) -> str:
        compression_service: CompressionBase = service.get_service("compression_service")
        encryption_service: EncryptionBase = service.get_service("encryption_service")
        filetype_service: FiletypeBase = service.get_service("filetype_service")
        return filetype_service.get_extension() + compression_service.get_extension() + encryption_service.get_extension()

    @abstractmethod
    def upload(self, data: Generator[bytes,None,None], report_manager: ReportManager) -> tuple[bool, str, Any]:
        '''
        upload_reporting is a queue that will be used to send information about the upload
        The information will be a dictionary with the following keys:
        - "type": str
        - "worker": int
        - "status": str        
        '''

    @abstractmethod
    def download(self, data: str, report_manager: ReportManager) -> Generator[bytes,None,None]:
        pass
