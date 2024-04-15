import lzma
from typing import Generator
from services.compression.compression_base import CompressionBase

class CompressionServiceLzma(CompressionBase):
    def compress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        print("Compressing data with LZMA in chunks")
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64)
        original_data_amount = 0
        compressed_data_amount = 0
        for chunk in data:
            original_data_amount += len(chunk)
            compressed_data = compressor.compress(chunk)
            compressed_data_amount += len(compressed_data)
            compression_ratio = compressed_data_amount/original_data_amount*100
            print(f"Compressed {original_data_amount} bytes to {compressed_data_amount} bytes. This is {compression_ratio}% of the original size.")
            yield compressed_data
        yield compressor.flush()


    def decompress(self, data: Generator[bytes,None,None]) -> Generator[bytes,None,None]:
        decompressor = lzma.LZMADecompressor()
        for chunk in data:
            yield decompressor.decompress(chunk)

    def get_extension(self) -> str:
        return ".xz"
