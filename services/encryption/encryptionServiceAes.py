from typing import Generator
from services.encryption.encryptionBase import EncryptionBase

class EncryptionServiceAes(EncryptionBase):
    def encrypt(self, data: Generator, key: str) -> Generator:
        return data

    def decrypt(self, data: Generator, key: str)-> Generator:
        return data

    def getExtension(self) -> str:
        return ".aes"
