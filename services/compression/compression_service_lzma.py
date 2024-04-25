import lzma
from typing import Generator
from services.compression.compression_base import CompressionBase

class CompressionServiceLzma(CompressionBase):
    compression_level: int
    def __init__(self, compression_level: int = 6) -> None:
        if compression_level not in range(1, 10):
            raise ValueError("Compression level must be between 1 and 9")
        self.compression_level = compression_level
        super().__init__()

    def compress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        print("Compressing data with LZMA in chunks")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=self.compression_level)
        for chunk in data:
            yield compressor.compress(chunk)
        yield compressor.flush()


    def decompress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        decompressor = lzma.LZMADecompressor()
        for chunk in data:
            yield decompressor.decompress(chunk)

    def get_extension(self) -> str:
        return ".xz"
