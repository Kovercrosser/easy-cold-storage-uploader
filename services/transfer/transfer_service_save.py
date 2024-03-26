from datetime import datetime
from typing import Generator
from dependencyInjection.service import Service
from services.transfer.transfer_base import TransferBase

class TransferServiceSave(TransferBase):
    service: Service
    def __init__(self,  service: Service) -> None:
        self.service = service
        super().__init__()

    def upload(self, data: Generator):
        date:str = datetime.now().strftime("%Y-%m-%d")
        fileName:str = date + self.get_file_extension(self.service)
        size:int = 0
        with open(fileName, 'wb') as file:
            for chunk in data:
                size += len(chunk)
                print(f"Writing {len(chunk)} bytes to {fileName}")
                file.write(chunk)
        print(f"Upload complete. {size} bytes written to {fileName}")

    def download(self, data: Generator):
        return data
