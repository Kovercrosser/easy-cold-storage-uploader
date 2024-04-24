from io import BufferedRandom
from typing import Generator

def get_file_size(temp_file: BufferedRandom) -> int:
    temp_file.seek(0, 2)
    size = temp_file.tell()
    temp_file.seek(0)
    return size

class CreateSplittedFilesFromGenerator:
    """
    This Class is used to create parts of a file from a generator.
    It is similar to a Generator but gives out the chunks in a file of a given size, instead of yielding the chunks.
    """
    remaining_bytes_from_last_part: bytes = bytes()
    generator_exhausted: bool = False
    total_read_bytes: int = 0
    total_written_bytes: int = 0
    has_returned: bool = False

    def create_next_upload_size_part(self, data: Generator[bytes,None,None], upload_size_bytes: int, temp_file: BufferedRandom) -> None:
        """
        This function reads data from a generator and writes it to a temporary file of a given size.
        
        :param data: Generator that yields bytes
        :param upload_size_bytes: Size of the part to be written to the temporary file
        :param temp_file: Temporary file to write the data to
        """
        current_written_bytes = 0

        if not temp_file:
            raise ValueError("temp_ile is not set")
        if upload_size_bytes <= 0:
            raise ValueError("upload_size_bytes must be greater than 0")

        chunk: bytes = bytes()
        while True:
            if len(self.remaining_bytes_from_last_part) < upload_size_bytes:
                try:
                    chunk = next(data)
                    self.total_read_bytes += len(chunk)
                    if len(chunk) == 0:
                        raise StopIteration
                except StopIteration as exception:
                    self.generator_exhausted = True
                    if len(self.remaining_bytes_from_last_part) == 0 and len(chunk) == 0:
                        if not self.has_returned:
                            temp_file.seek(0)
                            self.has_returned = True
                            return
                        size = get_file_size(temp_file)
                        if size == 0:
                            raise exception
                        temp_file.seek(0)
                        self.has_returned = True
                        return
            else:
                temp_file.write(self.remaining_bytes_from_last_part[:upload_size_bytes])
                current_written_bytes += upload_size_bytes
                self.total_written_bytes += upload_size_bytes
                self.remaining_bytes_from_last_part = self.remaining_bytes_from_last_part[upload_size_bytes:]
                temp_file.seek(0)
                self.has_returned = True
                return

            if len(self.remaining_bytes_from_last_part) > upload_size_bytes:
                temp_file.write(self.remaining_bytes_from_last_part[:upload_size_bytes])
                current_written_bytes += upload_size_bytes
                self.total_written_bytes += upload_size_bytes
                self.remaining_bytes_from_last_part = self.remaining_bytes_from_last_part[upload_size_bytes:]
                temp_file.seek(0)
                self.has_returned = True
                return

            # now self.remainingBytesFromLastPart is empty or smaller then uploadSizeBytes

            temp_file.write(self.remaining_bytes_from_last_part)
            current_written_bytes += len(self.remaining_bytes_from_last_part)
            self.total_written_bytes += len(self.remaining_bytes_from_last_part)
            self.remaining_bytes_from_last_part = bytes()
            max_write_size_allowed = upload_size_bytes - current_written_bytes

            if chunk:
                if len(chunk) > max_write_size_allowed:
                    temp_file.write(chunk[:max_write_size_allowed])
                    self.remaining_bytes_from_last_part = chunk[max_write_size_allowed:]
                    chunk = bytes()
                    current_written_bytes += max_write_size_allowed
                    self.total_written_bytes += max_write_size_allowed
                    temp_file.seek(0)
                    self.has_returned = True
                    return
                temp_file.write(chunk)
                current_written_bytes += len(chunk)
                self.total_written_bytes += len(chunk)
                chunk = bytes()

            if self.remaining_bytes_from_last_part == b"" and self.generator_exhausted and len(chunk) == 0:
                raise StopIteration
