from services.compression.compressionBase import CompressionBase

class CompressionServiceGzip(CompressionBase):
    def compress(self, data):
        return data

    def decompress(self, data):
        return data
