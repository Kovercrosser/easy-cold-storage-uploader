from stat import S_IFREG
from datetime import datetime
from stream_zip import stream_zip, ZIP_64
from services.filetype.filetypeBase import FiletypeBase


def getFileChunks(filepath):
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1024)  # Adjust chunk size as needed
            if not chunk:
                break
            yield chunk

def createZip(filenames):
    memberFiles = []
    for filename in filenames:
        modifiedAt = datetime.now()
        mode = S_IFREG | 0o600
        memberFiles.append(
            (filename, modifiedAt, mode, ZIP_64, getFileChunks(filename))
        )
    zippedChunks = stream_zip(memberFiles)
    return zippedChunks

class FiletypeServiceZip(FiletypeBase):
    def pack(self, files: list[str], chunkSize:int):
        if chunkSize < 512:
            raise ValueError("chunkSize must be at least 512")
        return createZip(files)
    

    def unpack(self, data):
        return data
