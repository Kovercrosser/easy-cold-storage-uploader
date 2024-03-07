import os
from typing import Any, Generator
from stat import S_IFREG
from datetime import datetime
from stream_zip import stream_zip, ZIP_64, zlib
from services.filetype.filetypeBase import FiletypeBase


class FiletypeServiceZip(FiletypeBase):

    compressionLevel:int
    chunkSize:int

    def __init__(self, compressionLevel:int, chunkSize:int ) -> None:
        if not 0 <= compressionLevel <= 9:
            raise ValueError("encryptionLevel must be between 0 and 10")
        self.compressionLevel = compressionLevel
        if chunkSize < 512:
            raise ValueError("chunkSize must be at least 512")
        self.chunkSize = chunkSize
        super().__init__()

    def pack(self, files: list[str]) -> Generator[bytes, Any, None]:
        memberFiles = []
        for file in files:
            modifiedAt:datetime
            secondsSinceModified:float
            try:
                secondsSinceModified = os.path.getmtime(file)
                modifiedAt = datetime.fromtimestamp(secondsSinceModified)
            except OSError:
                modifiedAt = datetime.now()

            mode = S_IFREG | 0o600
            memberFiles.append(
                (file, modifiedAt, mode, ZIP_64, open(file, "rb")) # pylint: disable=consider-using-with
            )
        zippedChunks = stream_zip(
            files=memberFiles, chunk_size=self.chunkSize, get_compressobj=lambda: zlib.compressobj(wbits=-zlib.MAX_WBITS, level=self.compressionLevel)
            )
        return zippedChunks


    def unpack(self, data):
        raise NotImplementedError("Unpacking zip files isnt currently supported.")

    def getExtension(self) -> str:
        return ".zip"
