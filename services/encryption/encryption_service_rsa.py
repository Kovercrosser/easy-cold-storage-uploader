from typing import Generator
from services.encryption.encryption_base import EncryptionBase
from services.service_base import ServiceBase
from utils.report_utils import ReportManager

class EncryptionServiceRsa(EncryptionBase, ServiceBase):
    def encrypt(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("RSA encryption is not implemented")

    def decrypt(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("RSA decryption is not implemented")

    def get_extension(self) -> str:
        return ".rsa"
