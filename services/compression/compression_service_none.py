from typing import Generator
from services.compression.compression_base import CompressionBase

class CompressionServiceNone(CompressionBase):
    def compress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        return data

    def decompress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        return data

    def get_extension(self) -> str:
        return ""
