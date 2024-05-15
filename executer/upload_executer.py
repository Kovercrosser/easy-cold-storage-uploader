import datetime
from typing import Any
from datatypes.transfer_services import TransferInformation
from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.db_service import DbService
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from services.setting_service import SettingService
from services.transfer.transfer_base import TransferBase
from utils.report_utils import ReportManager
from utils.storage_utils import get_all_files_from_directories_and_files
from utils.console_utils import console, print_error


class UploadDbEntry:
    upload_datetime_utc: str
    encryption: str
    compression: str
    filetype: str
    information: TransferInformation
    def __init__(self, upload_datetime_utc:str, encryption:str, compression:str, filetype:str, information:TransferInformation):
        self.upload_datetime_utc = upload_datetime_utc
        self.encryption = encryption
        self.compression = compression
        self.filetype = filetype
        self.information = information
        super().__init__()

    def as_dict(self) -> dict[str, Any]:
        d = {
            "upload_datetime_utc":  self.upload_datetime_utc,
            "encryption": self.encryption,
            "compression": self.compression,
            "filetype": self.filetype,
            "information": self.information.as_dict()
        }
        return d

def upload(service: Service, profile: str, paths: list[str]) -> int:
    setting_service: SettingService = service.get_service("setting_service")
    assert setting_service is not None
    vault = setting_service.read_settings(profile, "vault")
    transfer_service: TransferBase = service.get_service("transfer_service")
    compression_service: CompressionBase = service.get_service("compression_service")
    encryption_service: EncryptionBase = service.get_service("encryption_service")
    filetype_service: FiletypeBase = service.get_service("filetype_service")
    db_uploads_service: DbService = service.get_service("db_uploads_service")

    # Get all files from the given paths
    with console.status("[bold green]Gathering information about the files..."):
        files = get_all_files_from_directories_and_files(paths)
    if len(files) == 0:
        print_error(f"No files found in {paths}")
        return 1
    files_text = "files" if len(files) > 1 else "file"
    console.print(f"Trying to upload {len(files)} {files_text} to [bold purple]{vault}[/bold purple]"
                        f" using profile: [bold purple]{profile}[/bold purple]")

    status_report_manager= ReportManager(service)

    packed_generator = filetype_service.pack(files, status_report_manager)
    compressed_generator = compression_service.compress(packed_generator, status_report_manager)
    encrypted_generator = encryption_service.encrypt(compressed_generator, status_report_manager)
    upload_status, upload_information = transfer_service.upload(encrypted_generator,status_report_manager)

    status_report_manager.stop_reporting()


    if upload_status:
        assert upload_information is not None
        db_information = UploadDbEntry(
            upload_datetime_utc = str(datetime.datetime.now(datetime.UTC)),
            encryption = encryption_service.get_extension(),
            compression = compression_service.get_extension(),
            filetype = filetype_service.get_extension(),
            information = upload_information
        )
        db_uploads_service.get_context().insert(db_information.as_dict())
        return 0
    return 1
