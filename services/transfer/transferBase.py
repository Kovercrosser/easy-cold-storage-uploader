from abc import ABC, abstractmethod

class TransferBase(ABC):

    @abstractmethod
    def upload(self, data):
        pass

    @abstractmethod
    def download(self, data):
        pass
