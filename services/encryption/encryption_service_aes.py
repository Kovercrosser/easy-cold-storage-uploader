import os
from typing import Generator
import uuid
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from services.encryption.encryption_base import EncryptionBase
from utils.console_utils import print_error
from utils.report_utils import ReportManager, Reporting

class EncryptionServiceAes(EncryptionBase):
    def __init__(self, password: str, password_file: str) -> None:
        #TO-DO Implement password file
        #TO-DO remove hardcoded salt
        salt = b'\xa4nTc\x1f\xab\x94\xa1\xefEH\tv\x97G\xe0'
        if password == "" and password_file == "":
            raise ValueError("Password or passwordfile is required for AES encryption")
        if password_file != "":
            if os.path.isfile(password_file) is False:
                print_error("Password file does not exist")
                raise ValueError("Password file does not exist")
            with open(password_file, "r", encoding="utf-8") as f:
                password = f.readline().strip()
                if password == "":
                    print_error("Password file is empty")
                    raise ValueError("Password file is empty")
                print(password)
                if " " in password:
                    print_error("Password file contains spaces")
                    raise ValueError("Password file contains spaces")
        key = PBKDF2(password, salt, dkLen=32)
        self.cipher_encrypt = AES.new(key, AES.MODE_CFB)
        super().__init__()

    def encrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("crypter", report_uuid, "waiting"))
        chunkcount = 0
        for unencrypted in data:
            chunkcount += 1
            yield self.cipher_encrypt.encrypt(unencrypted)
            upload_reporting.add_report(Reporting("crypter", report_uuid, "working", "chunk: " + str(chunkcount)))
        upload_reporting.add_report(Reporting("crypter", report_uuid, "finished", "chunks: " + str(chunkcount)))

    def decrypt(self, data: Generator[bytes,None,None], key: str, upload_reporting: ReportManager)-> Generator[bytes,None,None]:
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("crypter", report_uuid, "waiting"))
        chunkcount = 0
        for encrypted in data:
            chunkcount += 1
            yield self.cipher_encrypt.decrypt(encrypted)
            upload_reporting.add_report(Reporting("crypter", report_uuid, "working", "chunk: " + str(chunkcount)))
        upload_reporting.add_report(Reporting("crypter", report_uuid, "finished", "chunks: " + str(chunkcount)))

    def get_extension(self) -> str:
        return ".aes"
