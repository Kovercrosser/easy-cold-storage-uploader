from abc import ABC, abstractmethod

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, data):
        pass

    @abstractmethod
    def unpack(self, data):
        pass
