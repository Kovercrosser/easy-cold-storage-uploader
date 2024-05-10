import os
from typing import Type

from tinydb import Query
from tinydb.table import Document
from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.compression.compression_service_bzip2 import CompressionServiceBzip2
from services.compression.compression_service_lzma import CompressionServiceLzma
from services.compression.compression_service_none import CompressionServiceNone
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
from services.transfer.transfer_service_glacier import TransferServiceGlacier
from services.transfer.transfer_service_save import TransferServiceSave
from utils.console_utils import print_error, print_success
from utils.report_utils import ReportManager

def _check_if_glacier_id(service: Service, download_id: str) -> bool:
    db_uploads_service: DbService = service.get_service("db_uploads_service")
    assert db_uploads_service
    db = db_uploads_service.get_context()
    search_result = db.search(Query().information.archive_id == download_id)
    return len(search_result) >= 1

def _get_archive_informations(service: Service, download_id: str) -> Document | None:
    db_uploads_service: DbService = service.get_service("db_uploads_service")
    assert db_uploads_service
    db = db_uploads_service.get_context()
    docs: Document | list[Document] | None
    if _check_if_glacier_id(service, download_id):
        docs = db.get(Query().information.archive_id == download_id)
    else:
        if not download_id.isnumeric():
            return None
        if not db.contains(doc_id=int(download_id)):
            return None
        docs =  db.get(doc_id=int(download_id))
    if isinstance(docs, list):
        return docs[0]
    return docs

def _file_ending_service_mapping(service: Service, encryption_ending: str, compression_ending: str, filetype_ending: str, transfer_type: str, password: str, password_file: str, location: str, file_name: str) -> list[tuple[str, ServiceBase]]:
    mapped_services: list[tuple[str, ServiceBase]] =  []
    match compression_ending:
        case ".bz2":
            mapped_services.append(("compression_service", CompressionServiceBzip2()))
        case ".xz":
            mapped_services.append(("compression_service", CompressionServiceLzma()))
        case "":
            mapped_services.append(("", CompressionServiceNone()))
        case _:
            raise ValueError("Compression not found.")
    match encryption_ending:
        case ".aes":
            mapped_services.append(("encryption_service", EncryptionServiceAes(password, password_file)))
        case ".rsa":
            mapped_services.append(("encryption_service", EncryptionServiceRsa()))
        case "":
            mapped_services.append(("none", EncryptionServiceNone()))
        case _:
            raise ValueError("Encryption not found.")
    match filetype_ending:
        case ".tar":
            mapped_services.append(("filetype_service", FiletypeServiceTar()))
        case ".zip":
            mapped_services.append(("filetype_service", FiletypeServiceZip(compression_level=0, chunk_size=10*1024*1024)))
        case "":
            mapped_services.append(("none", FiletypeServiceNone()))
        case _:
            raise ValueError("Filetype not found.")
    match transfer_type:
        case "save":
            mapped_services.append(("transfer_service", TransferServiceSave(service, location, file_name)))
        case "glacier":
            mapped_services.append(("transfer_service", TransferServiceGlacier(service)))
        case _:
            raise ValueError("Transfer type not found.")
    return mapped_services


def download(service: Service, profile: str, location:str, download_id:str, password:str, password_file:str) -> int:
    upload_information = _get_archive_informations(service, download_id)
    if upload_information is None:
        print_error("Download ID not found.")
        return 1

    services = _file_ending_service_mapping(
        service,
        str(upload_information.get("encryption")),
        str(upload_information.get("compression")),
        str(upload_information.get("filetype")),
        str(upload_information.get("type")),
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

    transfer_generator = transfer_service.download(upload_information, status_report_manager)
    encrypted_generator = encryption_service.decrypt(transfer_generator, status_report_manager)
    compressed_generator = compression_service.decompress(encrypted_generator, status_report_manager)
    filetype_service.unpack(compressed_generator, location, str(upload_information.get("filename")), status_report_manager)

    status_report_manager.stop_reporting()

    print_success(f"[bold green]Download completed. {upload_information}")
    return 0
