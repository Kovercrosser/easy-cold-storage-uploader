from abc import ABC, abstractmethod

class EncryptionBase(ABC):

    @abstractmethod
    def encrypt(self, data: bytes, key: str) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes, key: str) -> bytes:
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
