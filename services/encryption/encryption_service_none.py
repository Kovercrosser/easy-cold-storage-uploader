from typing import Generator
from services.encryption.encryption_base import EncryptionBase

class EncryptionServiceNone(EncryptionBase):
    def encrypt(self, data: Generator[bytes,None,None], key: str) -> Generator[bytes,None,None]:
        return data

    def decrypt(self, data: Generator[bytes,None,None], key: str) -> Generator[bytes,None,None]:
        return data

    def get_extension(self) -> str:
        return ""
