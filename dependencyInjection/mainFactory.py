from dependencyInjection.service import Service
from services.compression.compressionServiceNone import CompressionServiceNone
from services.compression.compressionServiceBzip2 import CompressionServiceBzip2
from services.compression.compressionServiceGzip import CompressionServiceGzip
from services.encryption.encryptionServiceNone import EncryptionServiceNone
from services.encryption.encryptionServiceAes import EncryptionServiceAes
from services.encryption.encryptionServiceRsa import EncryptionServiceRsa
from services.filetype.filetypeServiceNone import FiletypeServiceNone
from services.filetype.filetypeServiceTar import FiletypeServiceTar
from services.filetype.filetypeServiceZip import FiletypeServiceZip
from services.transfer.transferServiceDryrun import TransferServiceDryrun
from services.transfer.transferServiceGlacier import TransferServiceGlacier

from utils.storageUtils import readSettings

def setupFactoryFromParameters(service: Service, compression: str = "None", encryption: str = "None", filetype: str = "None", dryrun: bool = False):
    if compression == "None":
        service.setService(CompressionServiceNone(), "compressionService")
    if compression == "bzip2":
        service.setService(CompressionServiceBzip2(), "compressionService")
    if compression == "gzip":
        service.setService(CompressionServiceGzip(), "compressionService")

    if encryption == "None":
        service.setService(EncryptionServiceNone(), "encryptionService")
    if encryption == "aes":
        service.setService(EncryptionServiceAes(), "encryptionService")
    if encryption == "rsa":
        service.setService(EncryptionServiceRsa(), "encryptionService")

    if filetype == "None":
        service.setService(FiletypeServiceNone(), "filetypeService")
    if filetype == "tar":
        service.setService(FiletypeServiceTar(), "filetypeService")
    if filetype == "zip":
        service.setService(FiletypeServiceZip(), "filetypeService")

    if dryrun:
        service.setService(TransferServiceDryrun(), "transferService")
    else:
        service.setService(TransferServiceGlacier(), "transferService")

def setupFactoryFromStorage(service: Service, profile: str = "default"):
    if readSettings("global", "setup") is None:
        raise ValueError("Setup not done yet.")

    compression = readSettings(profile, "compression")
    encryption = readSettings(profile, "encryption")
    filetype = readSettings(profile, "filetype")
    setupFactoryFromParameters(service, compression, encryption, filetype)
