from typing import Generator
from services.compression.compression_base import CompressionBase
from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class CompressionServiceBzip2(CompressionBase, ServiceBase):
    def compress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("Bzip2 compression is not implemented")

    def decompress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("Bzip2 decompression is not implemented")

    def get_extension(self) -> str:
        return ".bz2"
