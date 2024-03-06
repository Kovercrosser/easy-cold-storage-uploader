from abc import ABC, abstractmethod
from dependencyInjection.service import Service

class TransferBase(ABC):

    @staticmethod
    def getFileExtension(service: Service) -> str:
        compressService = service.getService("compressionService")
        encryptionService = service.getService("encryptionService")
        filetypeService = service.getService("filetypeService")
        return filetypeService.getExtension() + compressService.getExtension() + encryptionService.getExtension()

    @abstractmethod
    def upload(self, data):
        pass

    @abstractmethod
    def download(self, data):
        pass
