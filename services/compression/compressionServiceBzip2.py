from services.compression.compressionBase import CompressionBase

class CompressionServiceBzip2(CompressionBase):
    def compress(self, data):
        return data

    def decompress(self, data):
        return data
