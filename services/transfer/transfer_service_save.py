from datetime import datetime
from typing import Any, Generator
import uuid
from dependency_injection.service import Service
from services.transfer.transfer_base import TransferBase
from utils.console_utils import print_error, print_success
from utils.data_utils import bytes_to_human_readable_size
from utils.report_utils import ReportManager, Reporting

class TransferServiceSave(TransferBase):
    service: Service
    def __init__(self,  service: Service) -> None:
        self.service = service
        super().__init__()

    def upload(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> tuple[bool, str, Any]:
        date:str = datetime.now().strftime("%Y-%m-%d")
        file_name:str = date + self.get_file_extension(self.service)
        size:int = 0
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("packer", report_uuid, "waiting"))
        try:
            with open(file_name, 'wb') as file:
                chunkcount = 0
                for chunk in data:
                    size += len(chunk)
                    chunkcount += 1
                    upload_reporting.add_report(Reporting("packer", report_uuid, "working", "chunk: " + str(chunkcount)))
                    file.write(chunk)
        except (FileExistsError, FileNotFoundError) as exception:
            upload_reporting.add_report(Reporting("packer", report_uuid, "failed"))
            print_error(f"An error occurred while writing to {file_name}. {exception}")
            return False, "", None
        upload_reporting.add_report(Reporting("packer", report_uuid, "finished", "size: " + bytes_to_human_readable_size(size)))
        print_success(f"Upload complete. {bytes_to_human_readable_size(size)} bytes written to {file_name}")
        return True, "save_to_disc", {"file_name": file_name, "size": size}

    def download(self, data: str) -> Generator[bytes,None,None]:
        try:
            with open(data, 'rb') as file:
                while True:
                    chunk = file.read(1024*1024*10)
                    if not chunk:
                        break
                    yield chunk
        except (FileExistsError, FileNotFoundError) as exception:
            print_error(f"An error occurred while reading from the data. {exception}")
            yield b""
