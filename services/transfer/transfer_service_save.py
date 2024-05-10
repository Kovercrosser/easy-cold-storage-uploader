import os
import uuid
from typing import Any, Generator

from tinydb.table import Document

from dependency_injection.service import Service
from services.transfer.transfer_base import TransferBase
from utils.console_utils import print_error, print_success
from utils.data_utils import bytes_to_human_readable_size
from utils.report_utils import Reporting, ReportManager


class TransferServiceSave(TransferBase):
    service: Service
    file_name: str
    location: str
    def __init__(self,  service: Service, location: str, file_name_without_extension: str) -> None:
        self.service = service
        self.file_name = file_name_without_extension
        self.location = location
        super().__init__()

    def upload(self, data: Generator[bytes,None,None], report_manager: ReportManager) -> tuple[bool, str, str, Any]:
        self.file_name:str = os.path.join(self.location, self.file_name + self.get_file_extension(self.service))
        size:int = 0
        report_uuid = uuid.uuid4()
        report_manager.add_report(Reporting("transferer", report_uuid, "waiting"))
        try:
            with open(self.file_name, 'wb') as file:
                chunk_count = 0
                for chunk in data:
                    size += len(chunk)
                    chunk_count += 1
                    report_manager.add_report(Reporting("transferer", report_uuid, "working", "chunk: " + str(chunk_count)))
                    file.write(chunk)
        except (FileExistsError, FileNotFoundError) as exception:
            report_manager.add_report(Reporting("packer", report_uuid, "failed"))
            print_error(f"An error occurred while writing to {self.file_name}. {exception}")
            return False, "", "", None
        report_manager.add_report(Reporting("transferer", report_uuid, "finished", "size: " + bytes_to_human_readable_size(size)))
        print_success(f"Upload complete. {bytes_to_human_readable_size(size)} written to {self.file_name}")
        return True, "save", self.file_name,  {"file_name": self.file_name, "size": size, "location": os.getcwd()}

    def download(self, data_information: Document, report_manager: ReportManager) -> Generator[bytes,None,None]:
        report_uuid = uuid.uuid4()
        report_manager.add_report(Reporting("transferer", report_uuid, "waiting"))
        file_name = data_information["information"]["file_name"]
        location = data_information["information"]["location"]
        assert isinstance(file_name, str)
        assert isinstance(location, str)
        assert os.path.isdir(location)
        assert os.path.isfile(os.path.join(location,file_name))
        try:
            with open(os.path.join(location,file_name), 'rb') as file:
                chunk_count = 0
                size = 0
                while True:
                    chunk = file.read(1024*1024*10)
                    if not chunk:
                        break
                    chunk_count += 1
                    size += len(chunk)
                    report_manager.add_report(Reporting("transferer", report_uuid, "working", "chunk: " + str(chunk_count)))
                    yield chunk
                report_manager.add_report(Reporting("transferer", report_uuid, "finished", "size: " + bytes_to_human_readable_size(size)))
        except (FileExistsError, FileNotFoundError) as exception:
            print_error(f"An error occurred while reading from the data. {exception}")
            yield b""
