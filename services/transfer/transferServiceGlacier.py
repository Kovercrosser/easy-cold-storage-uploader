from typing import Generator
from services.transfer.transferBase import TransferBase

class TransferServiceGlacier(TransferBase):
    def upload(self, data: Generator):
        return "data"

    def download(self, data: Generator):
        return data
