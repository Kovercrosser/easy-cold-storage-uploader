import lzma
from typing import Generator
from services.compression.compression_base import CompressionBase

class CompressionServiceLzma(CompressionBase):
    def compress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        print("Compressing data with LZMA in chunks")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64)
        for chunk in data:
            yield compressor.compress(chunk)
        yield compressor.flush()


    def decompress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        decompressor = lzma.LZMADecompressor()
        for chunk in data:
            yield decompressor.decompress(chunk)

    def get_extension(self) -> str:
        return ".xz"
