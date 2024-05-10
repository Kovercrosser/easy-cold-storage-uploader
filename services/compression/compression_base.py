from abc import abstractmethod
from typing import Generator

from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class CompressionBase(ServiceBase):

    @abstractmethod
    def compress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def decompress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
