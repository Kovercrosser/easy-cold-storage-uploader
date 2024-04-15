from abc import ABC, abstractmethod
from typing import Generator
from dependencyInjection.service import Service
from services.compression.compression_base import CompressionBase
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase

class TransferBase(ABC):

    @staticmethod
    def get_file_extension(service: Service) -> str:
        compression_service: CompressionBase = service.get_service("compression_service")
        encryption_service: EncryptionBase = service.get_service("encryption_service")
        filetype_service: FiletypeBase = service.get_service("filetype_service")
        return filetype_service.get_extension() + compression_service.get_extension() + encryption_service.get_extension()

    @abstractmethod
    def upload(self, data: Generator[bytes,None,None]) -> bool:
        pass

    @abstractmethod
    def download(self, data: Generator[bytes,None,None]) -> bool:
        pass
