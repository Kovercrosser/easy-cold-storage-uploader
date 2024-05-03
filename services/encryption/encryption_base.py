from abc import ABC, abstractmethod
from typing import Generator

from utils.report_utils import ReportManager

class EncryptionBase(ABC):

    @abstractmethod
    def encrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def decrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
