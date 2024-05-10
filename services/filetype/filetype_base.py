from abc import abstractmethod
from typing import Generator

from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class FiletypeBase(ServiceBase):

    @abstractmethod
    def pack(self, files: list[str], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def unpack(self, data:Generator[bytes,None,None], save_location:str, filename:str, upload_reporting: ReportManager)-> None:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
