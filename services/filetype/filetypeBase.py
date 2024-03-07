from abc import ABC, abstractmethod
from typing import Generator

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str]) -> Generator:
        pass

    @abstractmethod
    def unpack(self, data):
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
