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
from services.transfer.transfer_service_save import TransferServiceSave
from services.transfer.transfer_service_glacier import TransferServiceGlacier

from utils.storage_utils import read_settings

def setup_factory_from_parameters(
    service: Service,
    compression: str = "None",
    encryption: str = "None",
    filetype: str = "None",
    dryrun: bool = False) -> None:
    if compression == "None":
        service.set_service(CompressionServiceNone(), "compression_service")
    if compression == "bzip2":
        service.set_service(CompressionServiceBzip2(), "compression_service")
    if compression == "lzma":
        service.set_service(CompressionServiceLzma(), "compression_service")

    if encryption == "None":
        service.set_service(EncryptionServiceNone(), "encryption_service")
    if encryption == "aes":
        service.set_service(EncryptionServiceAes("Valeistdumm"), "encryption_service")
    if encryption == "rsa":
        service.set_service(EncryptionServiceRsa(), "encryption_service")

    if filetype == "None":
        service.set_service(FiletypeServiceNone(), "filetype_service")
    if filetype == "tar":
        service.set_service(FiletypeServiceTar(), "filetype_service")
    if filetype == "zip":
        service.set_service(FiletypeServiceZip(compression_level=0, chunk_size=10*1024*1024), "filetype_service")

    if dryrun:
        service.set_service(TransferServiceSave(service), "transfer_service")
    else:
        service.set_service(TransferServiceGlacier(service,  False, 64), "transfer_service")

    service.set_service(CancelService(), "cancel_service")
    service.set_service(DbService("uploads.json"), "db_uploads_service")
    service.set_service(DbService("downloads.json"), "db_downloads_service")

def setup_factory_from_storage(service: Service, profile: str = "default") -> None:
    if read_settings("global", "setup") is None:
        raise ValueError("Setup not done yet.")

    compression = read_settings(profile, "compression")
    encryption = read_settings(profile, "encryption")
    filetype = read_settings(profile, "filetype")
    if any([compression is None, encryption is None, filetype is None]):
        raise ValueError("Profile not setup correctly.")
    assert compression is not None
    assert encryption is not None
    assert filetype is not None
    setup_factory_from_parameters(service, compression, encryption, filetype)
