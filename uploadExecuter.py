from dependencyInjection.service import Service
from utils.storageUtils import getAllFilesFromDirectoriesAndFiles, readSettings


def upload(service: Service, profile: str, paths: list) -> int:
    vault = readSettings(profile, "vault")

    transferService = service.getService("transferService")
    compressService = service.getService("compressionService")
    # encryptionService = service.getService("encryptionService")
    filetypeService = service.getService("filetypeService")

    files = getAllFilesFromDirectoriesAndFiles(paths)
    print(f"Uploading {paths} to {vault}...")
    print(f"Trying to upload {len(files)} file(s) using profile: {profile}")

    value = filetypeService.pack(files)
    data = compressService.compress(value)
    transferService.upload(data)
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
