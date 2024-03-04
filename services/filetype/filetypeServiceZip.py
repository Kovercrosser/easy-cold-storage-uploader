from stat import S_IFREG
from datetime import datetime
from stream_zip import stream_zip, ZIP_64
from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceZip(FiletypeBase):
    def pack(self, files: list[str], chunkSize:int):
        if chunkSize < 512:
            raise ValueError("chunkSize must be at least 512")
        memberFiles = []
        for file in files:
            modifiedAt = datetime.now()
            mode = S_IFREG | 0o600
            memberFiles.append(
                (file, modifiedAt, mode, ZIP_64, open(file, "rb"))
            )
        zippedChunks = stream_zip(files=memberFiles, chunk_size=chunkSize)
        return zippedChunks


    def unpack(self, data):
        return data
