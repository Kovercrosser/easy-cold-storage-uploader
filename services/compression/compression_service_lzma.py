import lzma
from typing import Generator
import uuid
from services.compression.compression_base import CompressionBase
from utils.report_utils import ReportManager, Reporting

class CompressionServiceLzma(CompressionBase):
    compression_level: int
    def __init__(self, compression_level: int = 6) -> None:
        if compression_level not in range(1, 10):
            raise ValueError("Compression level must be between 1 and 9")
        self.compression_level = compression_level
        super().__init__()

    def compress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        print("Compressing data with LZMA in chunks")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=self.compression_level)
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("compressor", report_uuid, "waiting"))
        chunkcount = 0
        for chunk in data:
            chunkcount += 1
            yield compressor.compress(chunk)
            upload_reporting.add_report(Reporting("compressor", report_uuid, "working", "chunk: " + str(chunkcount)))
        yield compressor.flush()
        upload_reporting.add_report(Reporting("compressor", report_uuid, "finished", "chunks: " + str(chunkcount)))


    def decompress(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        decompressor = lzma.LZMADecompressor()
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("compressor", report_uuid, "waiting"))
        chunkcount = 0
        for chunk in data:
            chunkcount += 1
            yield decompressor.decompress(chunk)
            upload_reporting.add_report(Reporting("compressor", report_uuid, "working", "chunk: " + str(chunkcount)))
        upload_reporting.add_report(Reporting("compressor", report_uuid, "finished", "chunks: " + str(chunkcount)))

    def get_extension(self) -> str:
        return ".xz"
