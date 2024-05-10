from typing import Generator
from services.compression.compression_base import CompressionBase
from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class CompressionServiceNone(CompressionBase, ServiceBase):
    def compress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        return data

    def decompress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        return data

    def get_extension(self) -> str:
        return ""
