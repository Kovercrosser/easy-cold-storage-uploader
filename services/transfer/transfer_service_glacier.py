import datetime
import hashlib
import multiprocessing as mp
import tempfile
import time
import uuid
from io import BufferedRandom
from typing import Any, Generator, Tuple, Union
import boto3
import botocore.client
from datatypes.transfer_services import TransferInformation, TransferServiceType
from dependency_injection.service import Service
from services.cancel_service import CancelService
from services.service_base import ServiceBase
from services.setting_service import SettingService
from services.transfer.transfer_base import TransferBase
from utils.console_utils import console, print_error, print_success, print_warning
from utils.data_utils import (CreateSplittedFilesFromGenerator,
                              bytes_to_human_readable_size, get_file_size)
from utils.hash_utils import compute_sha256_tree_hash_for_aws
from utils.report_utils import Reporting, ReportManager

class GlacierInformation(TransferInformation):
    def __init__(self, dryrun: bool, region: str, vault: str, file_name: str, archive_id: str, checksum: str, size_in_bytes: int, human_readable_size: str, upload_id: str, location: str) -> None:
        self.dryrun: bool = dryrun
        self.region: str = region
        self.vault: str =  vault
        self.archive_id: str = archive_id
        self.checksum: str = checksum
        self.size_in_bytes: int = size_in_bytes
        self.human_readable_size: str =  human_readable_size
        self.upload_id: str = upload_id
        self.location: str = location
        super().__init__(file_name, TransferServiceType.GLACIER)
    def as_dict(self) -> dict[str, Any]:
        d = super().as_dict()
        d["dryrun"] = self.dryrun
        d["region"] = self.region
        d["vault"] = self.vault
        d["archive_id"] = self.archive_id
        d["checksum"] = self.checksum
        d["size_in_bytes"] = self.size_in_bytes
        d["human_readable_size"] = self.human_readable_size
        d["upload_id"] = self.upload_id
        d["location"] = self.location
        return d

class TransferServiceGlacier(TransferBase, ServiceBase):
    service: Service
    upload_size: int
    dryrun: bool
    hashes: list[bytes] = []
    upload_consumer_processes: list[mp.Process] = []

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

    def upload(self, data: Generator[bytes,None,None], report_manager: ReportManager) -> tuple[bool, TransferInformation | None]:
        setting_service: SettingService = self.service.get_service("setting_service")
        region:str | None = setting_service.read_settings("default", "region")
        vault:str | None = setting_service.read_settings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        glacier_client: botocore.client.BaseClient = boto3.client("glacier", region_name=region)
        cancel_service: CancelService = self.service.get_service("cancel_service")
        file_name:str = datetime.datetime.now().strftime("%Y-%m-%d") + self.get_file_extension(self.service)
        assert region is not None
        assert vault is not None
        upload_id, location, cancel_uuid = self.__init_upload(
            file_name=file_name,
            vault=vault,
            region=region,
            cancel_service=cancel_service,
            glacier_client=glacier_client
        )

        # Upload the parts
        try:
            upload_total_size_in_bytes: int = self.__upload_parts(data, upload_id, vault, report_manager, glacier_client)
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            print_error("Error during upload")
            self.cancel_upload("Error during upload", glacier_client, vault, upload_id)
            cancel_service.unsubscribe_from_cancel_event(cancel_uuid)
            return False, None
        if upload_total_size_in_bytes == -1:
            self.cancel_upload("User Interrupt", glacier_client, vault, upload_id)
            cancel_service.unsubscribe_from_cancel_event(cancel_uuid)
            return False, None
        # Finish the upload
        try:
            archive_id, checksum = self.__finish_upload(upload_id, vault, upload_total_size_in_bytes, report_manager, cancel_service, cancel_uuid, glacier_client)
        except Exception:
            print_error("Error during finishing the upload")
            self.cancel_upload("Error during finishing the upload", glacier_client, vault, upload_id)
            cancel_service.unsubscribe_from_cancel_event(cancel_uuid)
            return False, None
        info = GlacierInformation(
            dryrun=self.dryrun,
            region=region,
            vault=vault,
            file_name=file_name,
            archive_id=archive_id,
            checksum=checksum,
            size_in_bytes=upload_total_size_in_bytes,
            human_readable_size=bytes_to_human_readable_size(upload_total_size_in_bytes),
            upload_id=upload_id,
            location=location
        )
        return True, info

    def __finish_upload(self, upload_id: str, vault: str, upload_total_size_in_bytes: int, report_manager: ReportManager, cancel_service: CancelService, cancel_uuid: uuid.UUID, glacier_client: botocore.client.BaseClient) -> tuple[str, str]:
        assert glacier_client is not None
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
            cancel_service.unsubscribe_from_cancel_event(cancel_uuid)
            uuid_finish_up = uuid.uuid4()
            report_manager.add_report(Reporting("transferer", uuid_finish_up, "working", "Finishing up..."))
            assert hasattr(glacier_client, 'complete_multipart_upload')
            complete_status = glacier_client.complete_multipart_upload( # type: ignore
                vaultName=vault,
                uploadId=upload_id,
                archiveSize=str(upload_total_size_in_bytes),
                checksum=checksum
            )
            report_manager.add_report(Reporting("transferer", uuid_finish_up, "finished", "Finishing up..."))
        archive_id = complete_status['archiveId']
        assert archive_id is not None and isinstance(archive_id, str)
        print_success(f"Finished Uploading. Archive ID: [bold purple]{archive_id}")
        return archive_id, checksum

    def __init_upload(self, file_name:str, vault:str, region:str, cancel_service: CancelService, glacier_client: botocore.client.BaseClient) -> Tuple[str, str, uuid.UUID]:
        if self.dryrun:
            console.print(f"DRY RUN: Uploading {file_name} to Glacier vault {vault} in {region} region with {self.upload_size} byte parts")
            creation_response = {
                'uploadId': 'DRY_RUN_UPLOAD_ID',
                'location': 'DRY_RUN_LOCATION'
            }
        else:
            assert hasattr(glacier_client, 'initiate_multipart_upload')
            creation_response = glacier_client.initiate_multipart_upload( # type: ignore
                vaultName=vault,
                archiveDescription=f'{file_name}',
                partSize=str(self.upload_size)
            )
        cancel_uuid = cancel_service.subscribe_to_cancel_event(self.cancel_upload, glacier_client=glacier_client, vault=vault, upload_id=str(creation_response['uploadId']))
        return creation_response['uploadId'] , creation_response['location'], cancel_uuid

    def __upload_consumer(self, queue: "mp.Queue[dict[str, Union[str, int, bytes]]]", upload_id: str, vault: str, upload_reporting: ReportManager, glacier_client: botocore.client.BaseClient) -> None:
        report_uuid = uuid.uuid4()
        upload_reporting.add_report(Reporting("transferer", report_uuid, "waiting"))
        while True:
            if queue.empty():
                upload_reporting.add_report(Reporting("transferer", report_uuid, "waiting"))
                try:
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
                continue
            try:
                data = queue.get(timeout=1)
            except Exception:
                continue
            if data["range"] == "finish":
                queue.put({"range": "finish", "part": 0, "data": b""}) # add it again to the queue to notify the other consumers
                upload_reporting.add_report(Reporting("transferer", report_uuid, "finished"))
                break
            if not isinstance(data, dict) or not isinstance(data["data"], bytes) or not isinstance(data["range"], str) or not isinstance(data["part"], int):
                continue
            upload_reporting.add_report(Reporting("transferer", report_uuid, "working", f"uploading Part {str(data["part"] + 1)}"))
            try:
                assert hasattr(glacier_client, 'upload_multipart_part')
                glacier_client.upload_multipart_part( # type: ignore
                    vaultName=vault,
                    uploadId=upload_id,
                    body=data["data"],
                    range=data["range"]
                )

            except KeyboardInterrupt:
                break
            except Exception:
                print_error("Error while uploading a part")

    def __upload_parts(self, data: Generator[bytes,None,None], upload_id: str, vault: str, upload_reporting: ReportManager, glacier_client: botocore.client.BaseClient) -> int:
        upload_total_size_in_bytes = 0
        creater = CreateSplittedFilesFromGenerator()
        uploaded_parts = 0
        queue: mp.Queue[dict[str, Union[str, int, bytes]]] = mp.Queue()
        amount_of_consumer_processes = 2
        for _ in range(amount_of_consumer_processes):
            process = mp.Process(target=self.__upload_consumer, args=(queue, upload_id, vault, upload_reporting, glacier_client))
            process.daemon = True
            process.start()
            self.upload_consumer_processes.append(process)
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
        for process in self.upload_consumer_processes:
            process.join()
        return upload_total_size_in_bytes

    def cancel_upload(self, reason: str, glacier_client: botocore.client.BaseClient, vault: str = "", upload_id: str = "") -> None:
        if not self.dryrun:
            for process in self.upload_consumer_processes:
                process.terminate()
            self.upload_consumer_processes = []
            if vault == "" or upload_id == "":
                print("Aborting all uploads")
                assert hasattr(glacier_client, 'abort_multipart_upload')
                glacier_client.abort_multipart_upload(vaultName=vault, uploadId=upload_id) # type: ignore
                print_warning(f"Uploaded Parts removed on remote because of {reason}")

    def download(self, data_information: TransferInformation, report_manager: ReportManager) -> Generator[bytes,None,None]:
        setting_service = self.service.get_service("setting_service")
        region:str | None = setting_service.read_settings("default", "region")
        vault:str | None = setting_service.read_settings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        glacier_client = boto3.client("glacier", region_name=region)
        cancel_service = self.service.get_service("cancel_service")
        raise NotImplementedError("Downloading files isnt currently supported.")
