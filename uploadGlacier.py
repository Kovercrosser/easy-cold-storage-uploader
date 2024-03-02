from dependencyInjection.service import Service
from utils.storageUtils import getAllFilesFromDirectoriesAndFiles, readSettings


def upload(service: Service, profile: str, paths: list) -> int:
    vault = readSettings(profile, "vault")
    print(f"Uploading {paths} to {vault}...")

    transferService = service.getService("transferService")
    # compressService = service.getService("compressionService")
    # encryptionService = service.getService("encryptionService")
    filetypeService = service.getService("filetypeService")

    files = getAllFilesFromDirectoriesAndFiles(paths)

    value = filetypeService.pack(files, 1024*1024)

    transferService.upload(value)
    # print(f"Uploading {len(value)} bytes.")
    # transferService.upload(value)
    # transferService.upload(stream)
    # data = compressService.compress(data)
    # print(f"Compressed to {len(data)} bytes.")
    # data = encryptionService.encrypt(data, "SimpleKey4AES128")
    # print(f"Encrypted to {len(data)} bytes.")
    # transferService.upload(data)

    print("Upload complete.")
    return -1
