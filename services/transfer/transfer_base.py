from abc import ABC, abstractmethod
from typing import Generator
from dependencyInjection.service import Service

class TransferBase(ABC):

    @staticmethod
    def get_file_extension(service: Service) -> str:
        compression_service = service.get_service("compressionService")
        encryption_service = service.get_service("encryptionService")
        filetype_service = service.get_service("filetypeService")
        return filetype_service.get_extension() + compression_service.get_extension() + encryption_service.get_extension()

    @abstractmethod
    def upload(self, data: Generator):
        pass

    @abstractmethod
    def download(self, data: Generator):
        pass
