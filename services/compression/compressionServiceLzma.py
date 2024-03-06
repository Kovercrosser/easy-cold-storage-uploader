import lzma
from services.compression.compressionBase import CompressionBase

class CompressionServiceLzma(CompressionBase):
    def compress(self, data):
        print("Compressing data with LZMA")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64)
        originalDataAmount = 0
        compressedDataAmount = 0
        for chunk in data:
            originalDataAmount += len(chunk)
            compressedData = compressor.compress(chunk)
            compressedDataAmount += len(compressedData)
            print(f"Compressed {len(chunk)} bytes to {len(compressedData)} bytes. this is {compressedDataAmount/originalDataAmount*100}% of the original size.")
            yield compressedData
        compressor.flush()

    def decompress(self, data):
        return data
