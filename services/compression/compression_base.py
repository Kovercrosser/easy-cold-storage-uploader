from abc import ABC, abstractmethod
from typing import Generator

class CompressionBase(ABC):

    @abstractmethod
    def compress(self, data: Generator) -> Generator:
        pass

    @abstractmethod
    def decompress(self, data: Generator) -> Generator:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
