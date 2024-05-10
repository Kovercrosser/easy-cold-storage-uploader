from abc import abstractmethod
from typing import Generator

from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class EncryptionBase(ServiceBase):

    @abstractmethod
    def encrypt(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def decrypt(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass
