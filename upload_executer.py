from dependencyInjection.service import Service
from services.compression.compression_base import CompressionBase
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from services.transfer.transfer_base import TransferBase
from utils.storage_utils import get_all_files_from_directories_and_files, read_settings


def upload(service: Service, profile: str, paths: list) -> int:
    vault = read_settings(profile, "vault")

    transfer_service: TransferBase = service.get_service("transferService")
    compression_service: CompressionBase = service.get_service("compressionService")
    encryption_service: EncryptionBase = service.get_service("encryptionService")
    filetype_service: FiletypeBase = service.get_service("filetypeService")

    files = get_all_files_from_directories_and_files(paths)
    print(f"Uploading {paths} to {vault}...")
    print(f"Trying to upload {len(files)} file(s) using profile: {profile}")

    packed_generator = filetype_service.pack(files)
    compressed_generator = compression_service.compress(packed_generator)
    encrypted_generator = encryption_service.encrypt(compressed_generator, "")
    transfer_service.upload(encrypted_generator)

    print("Upload complete.")
    return -1
