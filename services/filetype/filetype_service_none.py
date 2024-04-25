from typing import Generator
from services.filetype.filetype_base import FiletypeBase

class FiletypeServiceNone(FiletypeBase):
    def pack(self, files: list[str]) -> Generator[bytes,None,None]:
        raise NotImplementedError("The Upload of individual Files isnt currently supported.")

    def unpack(self, data: Generator[bytes,None,None], save_location:str, filename:str)-> None:
        raise NotImplementedError("Unsupported")

    def get_extension(self) -> str:
        return ""
