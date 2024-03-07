from abc import ABC, abstractmethod
from typing import Generator

class EncryptionBase(ABC):

    @abstractmethod
    def encrypt(self, data: Generator, key: str) -> Generator:
        pass

    @abstractmethod
    def decrypt(self, data: Generator, key: str) -> Generator:
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
