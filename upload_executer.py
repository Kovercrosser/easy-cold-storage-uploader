import datetime
from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.db_service import DbService
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from services.transfer.transfer_base import TransferBase
from utils.storage_utils import get_all_files_from_directories_and_files, read_settings


def upload(service: Service, profile: str, paths: list[str]) -> int:
    rich_console = service.get_service("rich_console")
    vault = read_settings(profile, "vault")
    transfer_service: TransferBase = service.get_service("transfer_service")
    compression_service: CompressionBase = service.get_service("compression_service")
    encryption_service: EncryptionBase = service.get_service("encryption_service")
    filetype_service: FiletypeBase = service.get_service("filetype_service")
    db_uploads_service: DbService = service.get_service("db_uploads_service")

    # Get all files from the given paths
    with rich_console.status("[bold green]Gathering information about the files..."):
        files = get_all_files_from_directories_and_files(paths)
    if len(files) == 0:
        rich_console.print(f"[bold red]No files found in {paths}")
        return 1
    files_text = "files" if len(files) > 1 else "file"
    rich_console.print(f"Trying to upload {len(files)} {files_text} to [bold purple]{vault}[/bold purple]"
                        f" using profile: [bold purple]{profile}[/bold purple]")

    packed_generator = filetype_service.pack(files)
    compressed_generator = compression_service.compress(packed_generator)
    encrypted_generator = encryption_service.encrypt(compressed_generator, "")
    uplaod_status, upload_service, upload_information = transfer_service.upload(encrypted_generator)

    db_information = {"type": upload_service, "upload_datetime_utc":  datetime.datetime.now(datetime.UTC),"information": upload_information}

    if uplaod_status:
        db_uploads_service.get_context().insert(db_information)
        rich_console.print("[bold green]Upload completed.")
        return 0
    rich_console.print("[bold ]Upload failed.")
    return 1
