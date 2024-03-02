from abc import ABC, abstractmethod

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str], chunkSize:int):
        pass

    @abstractmethod
    def unpack(self, data):
        pass
