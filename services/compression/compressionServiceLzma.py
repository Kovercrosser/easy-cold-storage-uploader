import lzma
from typing import Generator
from services.compression.compressionBase import CompressionBase

class CompressionServiceLzma(CompressionBase):
    def compress(self, data: Generator) -> Generator:
        print("Compressing data with LZMA in chunks")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64)
        originalDataAmount = 0
        compressedDataAmount = 0
        for chunk in data:
            originalDataAmount += len(chunk)
            compressedData = compressor.compress(chunk)
            compressedDataAmount += len(compressedData)
            compressionRatio = compressedDataAmount/originalDataAmount*100
            print(f"Compressed {originalDataAmount} bytes to {compressedDataAmount} bytes. This is {compressionRatio}% of the original size.")
            yield compressedData
        yield compressor.flush()


    def decompress(self, data: Generator) -> Generator:
        decompressor = lzma.LZMADecompressor()
        for chunk in data:
            yield decompressor.decompress(chunk)

    def getExtension(self) -> str:
        return ".xz"
