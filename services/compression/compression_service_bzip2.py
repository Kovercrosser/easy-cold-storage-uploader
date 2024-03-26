from typing import Generator
from services.compression.compression_base import CompressionBase

class CompressionServiceBzip2(CompressionBase):
    def compress(self, data: Generator) -> Generator:
        return data

    def decompress(self, data: Generator) -> Generator:
        return data

    def get_extension(self) -> str:
        return ".bz2"
