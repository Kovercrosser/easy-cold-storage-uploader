from typing import Generator
from services.encryption.encryption_base import EncryptionBase
from utils.report_utils import ReportManager

class EncryptionServiceRsa(EncryptionBase):
    def encrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("RSA encryption is not implemented")

    def decrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("RSA decryption is not implemented")

    def get_extension(self) -> str:
        return ".rsa"
