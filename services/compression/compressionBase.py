from abc import ABC, abstractmethod

class CompressionBase(ABC):

    @abstractmethod
    def compress(self, data):
        pass

    @abstractmethod
    def decompress(self, data):
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
