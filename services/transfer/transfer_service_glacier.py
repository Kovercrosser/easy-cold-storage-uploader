from datetime import datetime
import hashlib
import multiprocessing as mp
from multiprocessing import Queue
from io import BufferedRandom
import tempfile
import time
from typing import Generator, Tuple, Union
import uuid
import boto3
from rich.console import Console
from rich.table import Table
from dependency_injection.service import Service
from services.cancel_service import CancelService
from services.transfer.transfer_base import TransferBase
from utils.hash_utils import compute_sha256_tree_hash_for_aws
from utils.storage_utils import read_settings

class CreateSplittedFilesFromGenerator:
    """
    This Class  is used to create parts of a file from a generator.
    It is similar to a Generator but gives out the chunks in a file of a given size, instead of yielding the chunks.
    """
    remaining_bytes_from_last_part: bytes = bytes()
    generator_exhausted: bool = False
    total_read_bytes: int = 0
    total_written_bytes: int = 0

    def create_next_upload_size_part(self, data: Generator[bytes,None,None], upload_size_bytes: int, temp_file: BufferedRandom) -> None:
        """
        This function reads data from a generator and writes it to a temporary file of a given size.
        
        :param data: Generator that yields bytes
        :param upload_size_bytes: Size of the part to be written to the temporary file
        :param temp_file: Temporary file to write the data to
        """
        current_written_bytes = 0

        if not temp_file:
            raise ValueError("tempFile is not set")
        if upload_size_bytes <= 0:
            raise ValueError("uploadSizeBytes must be greater than 0")

        chunk: bytes = bytes()
        while True:
            try:
                chunk = next(data)
                self.total_read_bytes += len(chunk)
            except StopIteration as exception:
                self.generator_exhausted = True
                if self.remaining_bytes_from_last_part == b"" and len(chunk) == 0:
                    raise exception

            if len(self.remaining_bytes_from_last_part) > upload_size_bytes:
                temp_file.write(self.remaining_bytes_from_last_part[:upload_size_bytes])
                current_written_bytes += upload_size_bytes
                self.total_written_bytes += upload_size_bytes
                self.remaining_bytes_from_last_part = self.remaining_bytes_from_last_part[upload_size_bytes:]
                temp_file.seek(0)
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
                    current_written_bytes += max_write_size_allowed
                    self.total_written_bytes += max_write_size_allowed
                    temp_file.seek(0)
                    return
                temp_file.write(chunk)
                current_written_bytes += len(chunk)
                self.total_written_bytes += len(chunk)

            if self.remaining_bytes_from_last_part == b"" and self.generator_exhausted:
                temp_file.seek(0)
                return

def human_readable_size(size: int) -> str:
    sizef = float(size)
    for unit in ("", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
        if abs(sizef) < 1024.0:
            return f"{sizef:3.1f} {unit}"
        sizef /= 1024.0
    return f"{sizef:.1f} Yi"

def get_file_size(temp_file: BufferedRandom) -> int:
    temp_file.seek(0, 2)
    size = temp_file.tell()
    temp_file.seek(0)
    return size

class TransferServiceGlacier(TransferBase):
    service: Service
    upload_size: int
    dryrun: bool
    hashes: list[bytes] = []
    cancel_service: CancelService
    rich_console: Console
    glacier_client = None
    cancel_uuid: uuid.UUID | None = None
    upload_consumer_process_1: mp.Process | None = None
    upload_consumer_process_2: mp.Process | None = None
    upload_consumer_status_reporter: mp.Process | None = None

    def __init__(self,  service: Service, dryrun: bool = False, upload_size_in_mb: int = 16) -> None:
        self.service = service
        self.dryrun = dryrun
        if (upload_size_in_mb & (upload_size_in_mb - 1)) != 0:
            raise ValueError("uploadSize must be a power of 2. This is a limitation of AWS Glacier.")
        if upload_size_in_mb < 1 or upload_size_in_mb > 4096:
            raise ValueError("uploadSize must be between 1 MB and 4096 MB. This is a limitation of AWS Glacier.")
        self.upload_size = upload_size_in_mb * 1024 * 1024
        super().__init__()

    def add_to_hash_list(self, file: BufferedRandom) -> None:
        file.seek(0)
        for data in iter(lambda: file.read(1024*1024), b""):
            self.hashes.append(hashlib.sha256(data).digest())
        file.seek(0)

    def upload(self, data: Generator[bytes,None,None]) -> bool:
        region:str | None = read_settings("default", "region")
        vault:str | None = read_settings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        self.glacier_client = boto3.client('glacier', region_name=region)
        self.cancel_service = self.service.get_service("cancel_service")
        self.rich_console = self.service.get_service("rich_console")
        file_name:str = datetime.now().strftime("%Y-%m-%d") + self.get_file_extension(self.service)
        assert region is not None
        assert vault is not None
        upload_id, location = self.__init_upload(file_name=file_name, vault=vault, region=region)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Upload ID", style="dim")
        table.add_column("Location", style="dim")
        table.add_row(upload_id, location)
        self.rich_console.print(table)

        # Upload the parts
        try:
            upload_total_size_in_bytes: int = self.__upload_parts(data, upload_id, vault)
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            self.rich_console.print("[bold red]Error during upload")
            self.rich_console.print_exception()
            self.cancel_upload("Error during upload", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False
        if upload_total_size_in_bytes == -1:
            self.cancel_upload("User Interrupt", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False
        # Finish the upload
        try:
            self.__finish_upload(upload_id, vault, upload_total_size_in_bytes)
        except Exception:
            self.rich_console.print("[bold red]Error during finishing the upload")
            self.rich_console.print_exception()
            self.cancel_upload("Error during finishing the upload", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False
        self.glacier_client = None
        return True

    def __finish_upload(self, upload_id: str, vault: str, upload_total_size_in_bytes: int) -> None:
        checksum = compute_sha256_tree_hash_for_aws(self.hashes)
        self.hashes = []
        if checksum == "" or checksum is None:
            raise Exception("Error calculating checksum. Upload cannot be completed")
        if self.dryrun:
            complete_status = {
                'archiveId': 'DRY_RUN_ARCHIVE_ID',
                'checksum': checksum
            }
        else:
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            with self.rich_console.status("[bold green]Finishing up..."):
                if self.glacier_client:
                    complete_status = self.glacier_client.complete_multipart_upload(
                        vaultName=vault,
                        uploadId=upload_id,
                        archiveSize=str(upload_total_size_in_bytes),
                        checksum=checksum
                    )
                else:
                    raise Exception("Internal Error: Glacier client is not set")
        self.rich_console.print(f"Archive ID: [bold green]{complete_status['archiveId']}")

    def __init_upload(self, file_name:str, vault:str, region:str) -> Tuple[str, str]:
        if self.dryrun:
            self.rich_console.print(f"DRY RUN: Uploading {file_name} to Glacier vault {vault} in {region} region with {self.upload_size} byte parts")
            creation_response = {
                'uploadId': 'DRY_RUN_UPLOAD_ID',
                'location': 'DRY_RUN_LOCATION'
            }
        else:
            if self.glacier_client:
                creation_response = self.glacier_client.initiate_multipart_upload(
                    vaultName=vault,
                    archiveDescription=f'{file_name}',
                    partSize=str(self.upload_size)
                )
            else:
                raise Exception("Internal Error: Glacier client is not set")
        self.cancel_uuid = self.cancel_service.subscribe_to_cancel_event(self.cancel_upload, vault, creation_response['uploadId'], self_reference=self)
        return creation_response['uploadId'] , creation_response['location']

    def __upload_consumer(self, queue: "mp.Queue[dict[str, Union[str, int, bytes]]]", upload_id: str, vault: str, status_queue: "mp.Queue[str]") -> None:
        try:
            while True:
                if queue.empty():
                    status_queue.put("waiting")
                    time.sleep(1)
                    continue
                data = queue.get()
                if data["range"] == "finish":
                    queue.put({"range": "finish", "part": 0, "data": b""}) # add it again to the queue to notify the other consumers
                    status_queue.put("finished")
                    break
                if not isinstance(data, dict) or not isinstance(data["data"], bytes) or not isinstance(data["range"], str) or not isinstance(data["part"], int):
                    continue
                status_queue.put(f"uploading Part {str(data["part"] + 1)}")
                try:
                    if self.glacier_client:
                        self.glacier_client.upload_multipart_part(
                            vaultName=vault,
                            uploadId=upload_id,
                            body=data["data"],
                            range=data["range"]
                        )
                    else:
                        raise Exception("Internal Error: Glacier client is not set")
                except Exception:
                    self.rich_console.print("[bold red]Error during a part upload.")
                    self.rich_console.print_exception()
        except (KeyboardInterrupt, SystemExit):
            return

    def __upload_parts(self, data: Generator[bytes,None,None], upload_id: str, vault: str) -> int:
        upload_total_size_in_bytes = 0
        creater = CreateSplittedFilesFromGenerator()
        uploaded_parts = 0
        queue: mp.Queue[dict[str, Union[str, int, bytes]]] = mp.Queue()
        status_queue_1: mp.Queue[str] = mp.Queue()
        status_queue_2: mp.Queue[str] = mp.Queue()
        self.upload_consumer_status_reporter = mp.Process(target=self.__upload_consumer_status_reporter, args=([status_queue_1, status_queue_2],))
        self.upload_consumer_process_1 = mp.Process(target=self.__upload_consumer, args=(queue, upload_id, vault, status_queue_1))
        self.upload_consumer_process_1.daemon = True
        self.upload_consumer_process_2 = mp.Process(target=self.__upload_consumer, args=(queue, upload_id, vault, status_queue_2))
        self.upload_consumer_process_2.daemon = True
        self.upload_consumer_process_1.start()
        self.upload_consumer_process_2.start()
        self.upload_consumer_status_reporter.start()
        while True:
            with tempfile.TemporaryFile(mode="b+w") as temp_file:
                while queue.qsize() > 1:
                    time.sleep(0.5)
                try:
                    creater.create_next_upload_size_part(data, self.upload_size, temp_file)
                    self.add_to_hash_list(temp_file)
                except StopIteration:
                    temp_file.close()
                    break
                temp_file_size = get_file_size(temp_file)
                if not self.dryrun:
                    queue.put({
                        "range": f"bytes {uploaded_parts * self.upload_size}-{(uploaded_parts * self.upload_size) + temp_file_size - 1}/*",
                        "part": uploaded_parts,
                        "data": temp_file.read()})
                upload_total_size_in_bytes += temp_file_size
            uploaded_parts += 1
        queue.put({"range": "finish", "part": 0, "data": b""})
        self.upload_consumer_process_1.join()
        self.upload_consumer_process_2.join()
        self.upload_consumer_status_reporter.join()
        return upload_total_size_in_bytes

    def __upload_consumer_status_reporter(self, status_queues: "list[mp.Queue[str]]") -> None:
        with self.rich_console.status("") as status:
            old_values = ["" for _ in status_queues]
            finished: int = 0
            while True:
                new_values = []
                for queue in status_queues:
                    if not queue.empty():
                        new_values.append(queue.get())
                    else:
                        new_values.append("")
                for i, new_value in enumerate(new_values):
                    if new_value:
                        if new_value == "finished":
                            finished += 1
                        old_value = old_values[i]
                        old_values[i] = new_value
                        if old_value and old_value != "waiting":
                            self.rich_console.print(f"[purple][{datetime.now().strftime('%H:%M:%S')}][/purple] {old_value.replace("uploading ", "")} finished")
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Worker", justify="center")
                table.add_column("Status", justify="center")
                for index, value in enumerate(old_values):
                    table.add_row(f"{index + 1}", value, style="bold green")
                status.update(table)
                if finished == len(status_queues):
                    break
                time.sleep(0.1)

    def cancel_upload(self, reason: str, vault: str = "", upload_id: str = "") -> None:
        self.cancel_uuid = None
        if not self.dryrun:
            if self.upload_consumer_process_1:
                print("Terminating Process 1")
                self.upload_consumer_process_1.kill()
                self.upload_consumer_process_1 = None
            if self.upload_consumer_process_2:
                print("Terminating Process 2")
                self.upload_consumer_process_2.kill()
                self.upload_consumer_process_2 = None
            if self.upload_consumer_status_reporter:
                print("Terminating Status Reporter")
                self.upload_consumer_status_reporter.kill()
                self.upload_consumer_status_reporter = None
            if vault == "" or upload_id == "":
                if self.glacier_client:
                    print("Aborting all uploads")
                    self.glacier_client.abort_multipart_upload(vaultName=vault, uploadId=upload_id)
                    self.rich_console.print(f"[bold red]Uploaded Parts removed on remote because of {reason}.")

    def download(self, data: Generator[bytes,None,None]) -> bool:
        raise NotImplementedError("Downloading files isnt currently supported.")
