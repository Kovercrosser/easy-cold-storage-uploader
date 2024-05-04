import datetime
import hashlib
import multiprocessing as mp
from io import BufferedRandom
import tempfile
import time
from typing import Any, Generator, Tuple, Union
import uuid
import boto3
from dependency_injection.service import Service
from services.cancel_service import CancelService
from services.transfer.transfer_base import TransferBase
from utils.console_utils import console, print_warning
from utils.console_utils import print_error
from utils.data_utils import CreateSplittedFilesFromGenerator, bytes_to_human_readable_size, get_file_size
from utils.hash_utils import compute_sha256_tree_hash_for_aws
from utils.report_utils import ReportManager, Reporting
from utils.storage_utils import read_settings

class TransferServiceGlacier(TransferBase):
    service: Service
    upload_size: int
    dryrun: bool
    hashes: list[bytes] = []
    cancel_service: CancelService
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

    def upload(self, data: Generator[bytes,None,None], upload_reporting: ReportManager) -> tuple[bool, str, Any]:
        region:str | None = read_settings("default", "region")
        vault:str | None = read_settings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        self.glacier_client = boto3.client('glacier', region_name=region)
        self.cancel_service = self.service.get_service("cancel_service")
        file_name:str = datetime.datetime.now().strftime("%Y-%m-%d") + self.get_file_extension(self.service)
        assert region is not None
        assert vault is not None
        upload_id, location = self.__init_upload(file_name=file_name, vault=vault, region=region)

        # Upload the parts
        try:
            upload_total_size_in_bytes: int = self.__upload_parts(data, upload_id, vault, upload_reporting)
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            print_error("Error during upload")
            self.cancel_upload("Error during upload", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False, "", None
        if upload_total_size_in_bytes == -1:
            self.cancel_upload("User Interrupt", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False, "", None
        # Finish the upload
        try:
            archive_id, checksum = self.__finish_upload(upload_id, vault, upload_total_size_in_bytes)
        except Exception:
            print_error("Error during finishing the upload")
            self.cancel_upload("Error during finishing the upload", vault, upload_id)
            if self.cancel_uuid:
                self.cancel_service.unsubscribe_from_cancel_event(self.cancel_uuid)
            self.glacier_client = None
            return False, "", None
        self.glacier_client = None
        return True, "aws_glacier", { "dryrun": self.dryrun, "region": region, "vault": vault, "file_name": file_name,
                        "archive_id": archive_id, "checksum": checksum,
                        "size_in_bytes": upload_total_size_in_bytes, "human_readable_size": bytes_to_human_readable_size(upload_total_size_in_bytes),
                        "upload_id": upload_id, "location": location }

    def __finish_upload(self, upload_id: str, vault: str, upload_total_size_in_bytes: int) -> tuple[str, str]:
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
            with console.status("[bold green]Finishing up..."):
                if self.glacier_client:
                    complete_status = self.glacier_client.complete_multipart_upload(
                        vaultName=vault,
                        uploadId=upload_id,
                        archiveSize=str(upload_total_size_in_bytes),
                        checksum=checksum
                    )
                else:
                    raise Exception("Internal Error: Glacier client is not set")
        archive_id = complete_status['archiveId']
        assert archive_id is not None and isinstance(archive_id, str)
        console.print(f"Archive ID: [bold green]{archive_id}")
        return archive_id, checksum

    def __init_upload(self, file_name:str, vault:str, region:str) -> Tuple[str, str]:
        if self.dryrun:
            console.print(f"DRY RUN: Uploading {file_name} to Glacier vault {vault} in {region} region with {self.upload_size} byte parts")
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

    def __upload_consumer(self, queue: "mp.Queue[dict[str, Union[str, int, bytes]]]", upload_id: str, vault: str, upload_reporting: ReportManager) -> None:
        report_uuid = uuid.uuid4()
        report_queue = upload_reporting.get_queue_directly()
        report_queue.put(Reporting("transferer", report_uuid, "waiting"))
        while True:
            if queue.empty():
                report_queue.put(Reporting("transferer", report_uuid, "waiting"))
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                continue
            try:
                data = queue.get(timeout=1)
            except Exception:
                continue
            if data["range"] == "finish":
                queue.put({"range": "finish", "part": 0, "data": b""}) # add it again to the queue to notify the other consumers
                report_queue.put(Reporting("transferer", report_uuid, "finished", "uploading parts"))
                break
            if not isinstance(data, dict) or not isinstance(data["data"], bytes) or not isinstance(data["range"], str) or not isinstance(data["part"], int):
                continue
            report_queue.put(Reporting("transferer", report_uuid, "working", f"uploading Part {str(data["part"] + 1)}"))
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
            except KeyboardInterrupt:
                break
            except Exception:
                print_error("Error while uploading a part")

    def __upload_parts(self, data: Generator[bytes,None,None], upload_id: str, vault: str, upload_reporting: ReportManager) -> int:
        upload_total_size_in_bytes = 0
        creater = CreateSplittedFilesFromGenerator()
        uploaded_parts = 0
        queue: mp.Queue[dict[str, Union[str, int, bytes]]] = mp.Queue()
        self.upload_consumer_process_1 = mp.Process(target=self.__upload_consumer, args=(queue, upload_id, vault, upload_reporting))
        self.upload_consumer_process_1.daemon = True
        self.upload_consumer_process_2 = mp.Process(target=self.__upload_consumer, args=(queue, upload_id, vault, upload_reporting))
        self.upload_consumer_process_2.daemon = True
        self.upload_consumer_process_1.start()
        self.upload_consumer_process_2.start()
        while True:
            with tempfile.TemporaryFile(mode="b+w") as temp_file:
                try:
                    while queue.qsize() > 1:
                        try:
                            time.sleep(0.5)
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    break
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
        return upload_total_size_in_bytes

    def cancel_upload(self, reason: str, vault: str = "", upload_id: str = "") -> None:
        self.cancel_uuid = None
        if not self.dryrun:
            if self.upload_consumer_process_1:
                print("Terminating Process 1")
                self.upload_consumer_process_1.close()
                self.upload_consumer_process_1 = None
            if self.upload_consumer_process_2:
                print("Terminating Process 2")
                self.upload_consumer_process_2.terminate()
                self.upload_consumer_process_2 = None
            if self.upload_consumer_status_reporter:
                print("Terminating Status Reporter")
                self.upload_consumer_status_reporter.terminate()
                self.upload_consumer_status_reporter = None
            if vault == "" or upload_id == "":
                if self.glacier_client:
                    print("Aborting all uploads")
                    self.glacier_client.abort_multipart_upload(vaultName=vault, uploadId=upload_id)
                    print_warning(f"Uploaded Parts removed on remote because of {reason}")

    def download(self, data:str, upload_reporting: ReportManager) -> Generator[bytes,None,None]:
        raise NotImplementedError("Downloading files isnt currently supported.")
