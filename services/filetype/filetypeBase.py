from abc import ABC, abstractmethod
from typing import Any, Generator

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str]) -> Generator[bytes, Any, None]:
        pass

    @abstractmethod
    def unpack(self, data):
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
