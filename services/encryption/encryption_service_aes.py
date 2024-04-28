from typing import Generator
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from services.encryption.encryption_base import EncryptionBase

class EncryptionServiceAes(EncryptionBase):
    def __init__(self, password: str, password_file: str) -> None:
        #TO-DO Implement password file
        #TO-DO remove hardcoded salt
        salt = b'\xa4nTc\x1f\xab\x94\xa1\xefEH\tv\x97G\xe0'
        key = PBKDF2(password, salt, dkLen=32)
        self.cipher_encrypt = AES.new(key, AES.MODE_CFB)
        super().__init__()

    def encrypt(self, data: Generator[bytes,None,None], key: str) -> Generator[bytes,None,None]:
        for unencrypted in data:
            yield self.cipher_encrypt.encrypt(unencrypted)

    def decrypt(self, data: Generator[bytes,None,None], key: str)-> Generator[bytes,None,None]:
        for encrypted in data:
            decrypted = self.cipher_encrypt.decrypt(encrypted)
            yield decrypted

    def get_extension(self) -> str:
        return ".aes"
