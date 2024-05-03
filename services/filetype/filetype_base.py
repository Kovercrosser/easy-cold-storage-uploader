from abc import ABC, abstractmethod
from typing import Generator

from utils.report_utils import ReportManager

class FiletypeBase(ABC):

    @abstractmethod
    def pack(self, files: list[str], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def unpack(self, data:Generator[bytes,None,None], save_location:str, filename:str, upload_reporting: ReportManager)-> None:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
