from dependency_injection.service import Service
from services.compression.compression_service_none import CompressionServiceNone
from services.compression.compression_service_bzip2 import CompressionServiceBzip2
from services.compression.compression_service_lzma import CompressionServiceLzma
from services.db_service import DbService
from services.encryption.encryption_service_none import EncryptionServiceNone
from services.encryption.encryption_service_aes import EncryptionServiceAes
from services.encryption.encryption_service_rsa import EncryptionServiceRsa
from services.filetype.filetype_service_none import FiletypeServiceNone
from services.filetype.filetype_service_tar import FiletypeServiceTar
from services.filetype.filetype_service_zip import FiletypeServiceZip
from services.cancel_service import CancelService
from services.setting_service import SettingService
from services.transfer.transfer_service_save import TransferServiceSave
from services.transfer.transfer_service_glacier import TransferServiceGlacier
from datetime import date

def setup_factory_from_parameters( # pylint: disable=too-many-arguments
    service: Service,
    compression: str = "none",
    encryption: str = "none",
    filetype: str = "none",
    transfer_method: str = "glacier",
    transfer_chunk_size: int = 64,
    dryrun: bool = False,
    compression_level: int = 6,
    password: str = "",
    password_file: str = ""
    ) -> None:
    if compression == "none":
        service.set_service(CompressionServiceNone(), "compression_service")
    if compression == "bzip2":
        service.set_service(CompressionServiceBzip2(), "compression_service")
    if compression == "lzma":
        service.set_service(CompressionServiceLzma(compression_level=compression_level), "compression_service")

    if encryption == "none":
        service.set_service(EncryptionServiceNone(), "encryption_service")
    if encryption == "aes":
        service.set_service(EncryptionServiceAes(password, password_file), "encryption_service")
    if encryption == "rsa":
        service.set_service(EncryptionServiceRsa(), "encryption_service")

    if filetype == "none":
        service.set_service(FiletypeServiceNone(), "filetype_service")
    if filetype == "tar":
        service.set_service(FiletypeServiceTar(), "filetype_service")
    if filetype == "zip":
        service.set_service(FiletypeServiceZip(compression_level=0, chunk_size=10*1024*1024), "filetype_service")

    if transfer_method == "save":
        current_date = date.today().strftime("%d-%m-%Y")
        service.set_service(TransferServiceSave(service, "", current_date), "transfer_service")
    if transfer_method == "glacier":
        service.set_service(TransferServiceGlacier(service, dryrun, transfer_chunk_size), "transfer_service")

    service.set_service(CancelService(), "cancel_service")
    service.set_service(DbService("uploads.json"), "db_uploads_service")
    service.set_service(DbService("downloads.json"), "db_downloads_service")

def setup_factory_from_storage(service: Service, profile: str = "default") -> None:
    setting_service: SettingService = service.get_service("setting_service")
    assert setting_service is not None

    if setting_service.read_settings("global", "setup") is None:
        raise ValueError("Setup not done yet.")

    compression = setting_service.read_settings(profile, "compression")
    compression_level = setting_service.read_settings(profile, "compression_level")
    encryption = setting_service.read_settings(profile, "encryption")
    filetype = setting_service.read_settings(profile, "filetype")
    transfer_method = setting_service.read_settings(profile, "transfer_method")
    transfer_chunk_size = setting_service.read_settings(profile, "transfer_chunk_size")
    password = setting_service.read_settings(profile, "password")
    password_file = setting_service.read_settings(profile, "password_file")
    if any([compression is None, encryption is None, filetype is None]):
        raise ValueError("Profile not setup correctly.")
    assert compression is not None
    assert compression_level is not None
    compression_level_int = int(compression_level)
    assert encryption is not None
    assert filetype is not None
    assert transfer_method is not None
    assert transfer_chunk_size is not None
    transfer_chunk_size_int = int(transfer_chunk_size)
    assert password is not None
    assert password_file is not None
    setup_factory_from_parameters(
        service,
        compression=compression,
        encryption=encryption,
        filetype=filetype,
        transfer_method=transfer_method,
        transfer_chunk_size=transfer_chunk_size_int,
        compression_level=compression_level_int,
        password=password,
        password_file=password_file
        )
