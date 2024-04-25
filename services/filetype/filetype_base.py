from abc import ABC, abstractmethod
from typing import Generator

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str]) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def unpack(self, data:Generator[bytes,None,None], save_location:str, filename:str)-> None:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
