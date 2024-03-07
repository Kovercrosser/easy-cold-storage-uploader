from dependencyInjection.service import Service
from services.compression.compressionBase import CompressionBase
from services.encryption.encryptionBase import EncryptionBase
from services.filetype.filetypeBase import FiletypeBase
from services.transfer.transferBase import TransferBase
from utils.storageUtils import getAllFilesFromDirectoriesAndFiles, readSettings


def upload(service: Service, profile: str, paths: list) -> int:
    vault = readSettings(profile, "vault")

    transferService: TransferBase = service.getService("transferService")
    compressService: CompressionBase = service.getService("compressionService")
    encryptionService: EncryptionBase = service.getService("encryptionService")
    filetypeService: FiletypeBase = service.getService("filetypeService")

    files = getAllFilesFromDirectoriesAndFiles(paths)
    print(f"Uploading {paths} to {vault}...")
    print(f"Trying to upload {len(files)} file(s) using profile: {profile}")

    packedGenerator = filetypeService.pack(files)
    compressedGenerator = compressService.compress(packedGenerator)
    encryptedGenerator = encryptionService.encrypt(compressedGenerator, "")
    transferService.upload(encryptedGenerator)

    print("Upload complete.")
    return -1
