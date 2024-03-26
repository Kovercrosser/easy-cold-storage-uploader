from typing import Generator
from services.encryption.encryption_base import EncryptionBase

class EncryptionServiceRsa(EncryptionBase):
    def encrypt(self, data: Generator, key: str) -> Generator:
        return data

    def decrypt(self, data: Generator, key: str) -> Generator:
        return data

    def get_extension(self) -> str:
        return ".rsa"
