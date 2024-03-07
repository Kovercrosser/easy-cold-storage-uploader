from typing import Generator
from services.compression.compressionBase import CompressionBase

class CompressionServiceBzip2(CompressionBase):
    def compress(self, data: Generator) -> Generator:
        return data

    def decompress(self, data: Generator) -> Generator:
        return data

    def getExtension(self) -> str:
        return ".bz2"
