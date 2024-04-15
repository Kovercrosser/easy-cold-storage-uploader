from abc import ABC, abstractmethod
from typing import Generator

class EncryptionBase(ABC):

    @abstractmethod
    def encrypt(self, data: Generator[bytes,None,None], key: str) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def decrypt(self, data: Generator[bytes,None,None], key: str) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
