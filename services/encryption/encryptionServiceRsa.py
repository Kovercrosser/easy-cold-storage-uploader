from services.encryption.encryptionBase import EncryptionBase

class EncryptionServiceRsa(EncryptionBase):
    def encrypt(self, data: bytes, key: str or bytes) -> bytes:
        return data

    def decrypt(self, data: bytes, key: str or bytes) -> bytes:
        return data
