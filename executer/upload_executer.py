import datetime
from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.db_service import DbService
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from services.transfer.transfer_base import TransferBase
from utils.report_utils import ReportManager
from utils.storage_utils import get_all_files_from_directories_and_files, read_settings
from utils.console_utils import console, print_error


def upload(service: Service, profile: str, paths: list[str]) -> int:
    vault = read_settings(profile, "vault")
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
    encrypted_generator = encryption_service.encrypt(compressed_generator, "", status_report_manager)
    uplaod_status, upload_service, upload_information = transfer_service.upload(encrypted_generator,status_report_manager)

    status_report_manager.stop_reporting()

    db_information = {"type": upload_service, "upload_datetime_utc":  str(datetime.datetime.now(datetime.UTC)),"information": upload_information}
    if uplaod_status:
        db_uploads_service.get_context().insert(db_information)
        return 0
    return 1
