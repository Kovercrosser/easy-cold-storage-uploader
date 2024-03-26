from typing import Generator
from services.filetype.filetype_base import FiletypeBase

class FiletypeServiceNone(FiletypeBase):
    def pack(self, files: list[str]) -> Generator:
        raise NotImplementedError("The Upload of individual Files isnt currently supported.")

    def unpack(self, data):
        raise NotImplementedError("Unsupported")

    def get_extension(self) -> str:
        return ""
