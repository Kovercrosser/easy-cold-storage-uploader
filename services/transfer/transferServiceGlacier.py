from services.transfer.transferBase import TransferBase

class TransferServiceGlacier(TransferBase):
    def upload(self, data):
        return "data"

    def download(self, data):
        return data
