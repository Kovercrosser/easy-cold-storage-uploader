from services.encryption.encryptionBase import EncryptionBase

class EncryptionServiceNone(EncryptionBase):
    def encrypt(self, data):
        return data

    def decrypt(self, data):
        return data
