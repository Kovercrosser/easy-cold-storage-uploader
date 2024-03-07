from typing import Any, Generator
from services.filetype.filetypeBase import FiletypeBase

class FiletypeServiceTar(FiletypeBase):
    def pack(self, files: list[str]) -> Generator[bytes, Any, None]:
        raise NotImplementedError("Packing into a tar files isnt currently supported.")

    def unpack(self, data):
        raise NotImplementedError("Unpacking tar files isnt currently supported.")

    def getExtension(self) -> str:
        return ".tar"
