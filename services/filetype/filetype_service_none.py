from typing import Generator
from services.filetype.filetype_base import FiletypeBase
from utils.report_utils import ReportManager

class FiletypeServiceNone(FiletypeBase):
    def pack(self, files: list[str], upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("The Upload of individual Files isnt currently supported.")

    def unpack(self, data: Generator[bytes,None,None], save_location:str, filename:str, upload_reporting: ReportManager)-> None:
        raise NotImplementedError("Unsupported")

    def get_extension(self) -> str:
        return ""
