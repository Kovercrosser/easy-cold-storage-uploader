import os
from pathlib import Path
from dependency_injection.service import Service
from services.compression.compression_base import CompressionBase
from services.encryption.encryption_base import EncryptionBase
from services.filetype.filetype_base import FiletypeBase
from services.transfer.transfer_base import TransferBase
from utils.console_utils import print_success

def download(service: Service, profile: str, location:str, download_file:str) -> int:
    transfer_service: TransferBase = service.get_service("transfer_service")
    compression_service: CompressionBase = service.get_service("compression_service")
    encryption_service: EncryptionBase = service.get_service("encryption_service")
    filetype_service: FiletypeBase = service.get_service("filetype_service")

    transfer_generator = transfer_service.download(os.path.join(os.path.curdir, download_file))
    encrypted_generator = encryption_service.decrypt(transfer_generator, "Valeistdumm")
    compressed_generator = compression_service.decompress(encrypted_generator)
    filetype_service.unpack(compressed_generator, location, Path(download_file).stem)

    print_success("[bold green]Download completed.")
    return 0
