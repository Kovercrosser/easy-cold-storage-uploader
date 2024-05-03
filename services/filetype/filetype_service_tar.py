from typing import Generator
from services.filetype.filetype_base import FiletypeBase
from utils.report_utils import ReportManager

class FiletypeServiceTar(FiletypeBase):
    def pack(self, files: list[str], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("Packing into a tar files isnt currently supported.")

    def unpack(self, data: Generator[bytes,None,None], save_location:str, filename:str, upload_reporting: ReportManager) -> None:
        raise NotImplementedError("Unpacking tar files isnt currently supported.")

    def get_extension(self) -> str:
        return ".tar"
