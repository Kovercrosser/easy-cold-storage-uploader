from services.transfer.transferBase import TransferBase

class TransferServiceDryrun(TransferBase):
    def upload(self, data):
        return data

    def download(self, data):
        return data
