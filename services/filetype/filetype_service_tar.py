from typing import Generator
from services.filetype.filetype_base import FiletypeBase

class FiletypeServiceTar(FiletypeBase):
    def pack(self, files: list[str]) -> Generator:
        raise NotImplementedError("Packing into a tar files isnt currently supported.")

    def unpack(self, data):
        raise NotImplementedError("Unpacking tar files isnt currently supported.")

    def get_extension(self) -> str:
        return ".tar"
