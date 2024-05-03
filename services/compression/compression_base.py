from abc import ABC, abstractmethod
from typing import Generator

from utils.report_utils import ReportManager

class CompressionBase(ABC):

    @abstractmethod
    def compress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def decompress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
