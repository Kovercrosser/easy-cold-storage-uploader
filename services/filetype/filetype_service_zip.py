import os
from typing import Generator
from stat import S_IFREG
from datetime import datetime
from stream_zip import stream_zip, ZIP_64, zlib # type: ignore
from stream_unzip import stream_unzip
from services.filetype.filetype_base import FiletypeBase
from utils.console_utils import print_warning


class FiletypeServiceZip(FiletypeBase):

    compression_level:int
    chunk_size:int

    def __init__(self, compression_level:int, chunk_size:int ) -> None:
        if not 0 <= compression_level <= 9:
            raise ValueError("encryptionLevel must be between 0 and 10")
        self.compression_level = compression_level
        if chunk_size < 512:
            raise ValueError("chunkSize must be at least 512")
        self.chunk_size = chunk_size
        super().__init__()

    def pack(self, files: list[str]) -> Generator[bytes,None,None]:
        member_files = []
        def read_file(fi: str) -> Generator[bytes, None, None]:
            with open(fi, 'rb') as f:
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        return
                    yield data
        for file in files:
            modified_at:datetime
            seconds_since_modified:float
            try:
                seconds_since_modified = os.path.getmtime(file)
                modified_at = datetime.fromtimestamp(seconds_since_modified)
            except OSError:
                modified_at = datetime.now()

            mode = S_IFREG | 0o600
            member_files.append(
                (file, modified_at, mode, ZIP_64, read_file(file)) # pylint: disable=consider-using-with
            )

        zipped_chunks:Generator[bytes, None, None] = stream_zip(
            files=member_files, chunk_size=self.chunk_size,
            get_compressobj=lambda: zlib.compressobj(wbits=-zlib.MAX_WBITS, level=self.compression_level)
            )
        return zipped_chunks


    def unpack(self, data: Generator[bytes,None,None], save_location:str, filename:str) -> None:
        print_warning("Unziping is currently unsupported. It will save the zip file instead")
        with open(os.path.join(save_location, filename), 'wb') as f:
            for chunk in data:
                f.write(chunk)

    def get_extension(self) -> str:
        return ".zip"
