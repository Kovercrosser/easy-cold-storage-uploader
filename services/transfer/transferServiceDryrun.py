from services.transfer.transferBase import TransferBase

class TransferServiceDryrun(TransferBase):
    def upload(self, data):
        size = 0
        with open('output.zip', 'wb') as f:
            for chunk in data:
                size += len(chunk)
                print(f"Writing {len(chunk)} bytes to output.tar.gzip.aes")
                f.write(chunk)
        print(f"Upload complete. {size} bytes written to output.zip")

    def download(self, data):
        return data
