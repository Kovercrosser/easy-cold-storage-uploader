from abc import ABC, abstractmethod

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str]):
        pass

    @abstractmethod
    def unpack(self, data):
        pass

    @abstractmethod
    def getExtension(self) -> str:
        pass
