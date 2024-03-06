from services.compression.compressionBase import CompressionBase

class CompressionServiceNone(CompressionBase):
    def compress(self, data):
        return data

    def decompress(self, data):
        return data

    def getExtension(self) -> str:
        return ""
