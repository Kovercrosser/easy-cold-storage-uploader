from tabnanny import check
from typing import Any
from tinydb import Query
from tinydb.table import Document

from datatypes.file_ending import FileEndingCompression, FileEndingEncryption, FileEndingFiletype
from datatypes.transfer_services import TransferInformation, TransferServiceType
from dependency_injection.service import Service
from distutils.command import upload
from services.compression.compression_base import CompressionBase
from services.compression.compression_service_bzip2 import \
    CompressionServiceBzip2
from services.compression.compression_service_lzma import \
    CompressionServiceLzma
from services.compression.compression_service_none import \
    CompressionServiceNone
from services.db_service import DbService
from services.encryption.encryption_base import EncryptionBase
from services.encryption.encryption_service_aes import EncryptionServiceAes
from services.encryption.encryption_service_none import EncryptionServiceNone
from services.encryption.encryption_service_rsa import EncryptionServiceRsa
from services.filetype.filetype_base import FiletypeBase
from services.filetype.filetype_service_none import FiletypeServiceNone
from services.filetype.filetype_service_tar import FiletypeServiceTar
from services.filetype.filetype_service_zip import FiletypeServiceZip
from services.service_base import ServiceBase
from services.transfer.transfer_base import TransferBase
from services.transfer.transfer_service_glacier import GlacierInformation, TransferServiceGlacier
from services.transfer.transfer_service_save import SaveInformation, TransferServiceSave
from utils.console_utils import print_error, print_success
from utils.report_utils import ReportManager


def _check_if_glacier_id(service: Service, download_id: str) -> list[Document] | None:
    db_uploads_service: DbService = service.get_service("db_uploads_service")
    assert db_uploads_service
    db = db_uploads_service.get_context()
    search_result = db.search(Query().information.archive_id == download_id)
    if len(search_result) >= 1:
        assert isinstance(search_result, list)
        return search_result
    return None

def _get_archive_informations(service: Service, download_id: str) -> Document | None:
    db_uploads_service: DbService = service.get_service("db_uploads_service")
    assert db_uploads_service
    db = db_uploads_service.get_context()
    docs: Document | list[Document] | None = _check_if_glacier_id(service, download_id)
    if docs is None:
        if not download_id.isnumeric():
            return None
        if not db.contains(doc_id=int(download_id)):
            return None
        docs =  db.get(doc_id=int(download_id))
    if isinstance(docs, list):
        return docs[0]
    return docs

def _file_ending_service_mapping(service: Service, encryption_ending: str, compression_ending: str, filetype_ending: str, upload_info: dict[str, Any], password: str, password_file: str, location: str, file_name: str) -> tuple[list[tuple[str, ServiceBase]], TransferInformation]:
    mapped_services: list[tuple[str, ServiceBase]] =  []
    match compression_ending:
        case FileEndingCompression.BZIP2.value:
            mapped_services.append(("compression_service", CompressionServiceBzip2()))
        case FileEndingCompression.LZMA.value:
            mapped_services.append(("compression_service", CompressionServiceLzma()))
        case FileEndingCompression.NONE.value:
            mapped_services.append(("", CompressionServiceNone()))
        case _:
            raise ValueError("Compression not found.")
    match encryption_ending:
        case FileEndingEncryption.AES.value:
            mapped_services.append(("encryption_service", EncryptionServiceAes(password, password_file)))
        case FileEndingEncryption.RSA.value:
            mapped_services.append(("encryption_service", EncryptionServiceRsa()))
        case FileEndingEncryption.NONE.value:
            mapped_services.append(("none", EncryptionServiceNone()))
        case _:
            raise ValueError("Encryption not found.")
    match filetype_ending:
        case FileEndingFiletype.TAR.value:
            mapped_services.append(("filetype_service", FiletypeServiceTar()))
        case FileEndingFiletype.ZIP.value:
            mapped_services.append(("filetype_service", FiletypeServiceZip(compression_level=0, chunk_size=10*1024*1024)))
        case FileEndingFiletype.NONE.value:
            mapped_services.append(("none", FiletypeServiceNone()))
        case _:
            raise ValueError("Filetype not found.")

    uploade_service_type = upload_info["upload_service"]
    assert uploade_service_type is not None and isinstance(uploade_service_type, str)
    match uploade_service_type:
        case TransferServiceType.SAVE.value:
            mapped_services.append(("transfer_service", TransferServiceSave(service, location, file_name)))
            file_name = upload_info["file_name"]
            assert isinstance(file_name, str)
            size = upload_info["size"]
            assert isinstance(size, int)
            location = upload_info["location"]
            assert isinstance(location, str)

            return mapped_services, SaveInformation(file_name, size, location)
        case TransferServiceType.GLACIER.value:
            mapped_services.append(("transfer_service", TransferServiceGlacier(service)))
            dryrun = upload_info["dryrun"]
            assert isinstance(dryrun, bool)
            region = upload_info["region"]
            assert isinstance(region, str)
            vault = upload_info["vault"]
            assert isinstance(vault, str)
            file_name = upload_info["file_name"]
            assert isinstance(file_name, str)
            archive_id = upload_info["archive_id"]
            assert isinstance(archive_id, str)
            checksum = upload_info["checksum"]
            assert isinstance(checksum, str)
            size_in_bytes = upload_info["size_in_bytes"]
            assert isinstance(size_in_bytes, int)
            human_readable_size = upload_info["human_readable_size"]
            assert isinstance(human_readable_size, str)
            upload_id = upload_info["upload_id"]
            assert isinstance(upload_id, str)
            location = upload_info["location"]
            assert isinstance(location, str)

            return mapped_services, GlacierInformation(dryrun, region, vault, file_name, archive_id, checksum, size_in_bytes, human_readable_size, upload_id, location)
        case _:
            raise ValueError("Transfer type not found.")
    assert False

def download(service: Service, profile: str, location:str, download_id:str, password:str, password_file:str) -> int:
    upload_information = _get_archive_informations(service, download_id)
    if upload_information is None:
        print_error("Download ID not found.")
        return 1
    info_dict = dict(upload_information)
    information = info_dict["information"]
    encryption = info_dict["encryption"]
    compression = info_dict["compression"]
    filetype = info_dict["filetype"]
    assert information is not None and isinstance(information, dict)
    assert encryption is not None and isinstance(encryption, str)
    assert compression is not None and isinstance(compression, str)

    services, transfer_information = _file_ending_service_mapping(
        service,
        encryption,
        compression,
        filetype,
        information,
        password,
        password_file,
        "",
        ""
        )
    for service_name, service_class in services:
        service.set_service(service_class, service_name)
    transfer_service: TransferBase = service.get_service("transfer_service")
    compression_service: CompressionBase = service.get_service("compression_service")
    encryption_service: EncryptionBase = service.get_service("encryption_service")
    filetype_service: FiletypeBase = service.get_service("filetype_service")

    status_report_manager= ReportManager(service)

    transfer_generator = transfer_service.download(transfer_information, status_report_manager)
    encrypted_generator = encryption_service.decrypt(transfer_generator, status_report_manager)
    compressed_generator = compression_service.decompress(encrypted_generator, status_report_manager)
    filetype_service.unpack(compressed_generator, location, transfer_information.file_name, status_report_manager)

    status_report_manager.stop_reporting()

    print_success(f"[bold green]Download completed. {transfer_information} written to {location}")
    return 0
