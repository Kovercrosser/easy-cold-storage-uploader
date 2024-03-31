from datetime import datetime
from io import BufferedRandom
import tempfile
from typing import Generator
import boto3
import botocore
from dependencyInjection.service import Service
from services.transfer.transfer_base import TransferBase
from utils.hash_utils import compute_sha256_tree_hash
from utils.storage_utils import read_settings

class TransferServiceGlacierFileCreater:
    remaining_bytes_from_last_part: bytes = bytes()
    generator_exhausted: bool = False
    total_read_bytes: int = 0
    total_written_bytes: int = 0

    def create_next_upload_size_part(self, data: Generator, upload_size_bytes: int, temp_file: BufferedRandom) -> BufferedRandom:
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
                return temp_file

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
                    return temp_file
                temp_file.write(chunk)
                current_written_bytes += len(chunk)
                self.total_written_bytes += len(chunk)

            if self.remaining_bytes_from_last_part == b"" and self.generator_exhausted:
                temp_file.seek(0)
                return temp_file


class TransferServiceGlacier(TransferBase):
    service: Service
    upload_size: int # in MB must be power of two e.g. 1, 2, 4, 8, 16, 32, 64, 128, 256, 512. Min 1MB, Max 4096MB
    dryrun: bool

    def __init__(self,  service: Service, dryrun: bool = False, upload_size_in_mb: int = 16) -> None:
        self.service = service
        self.dryrun = dryrun
        if (upload_size_in_mb & (upload_size_in_mb - 1)) != 0:
            raise ValueError("uploadSize must be a power of 2. This is a limitation of AWS Glacier.")
        if upload_size_in_mb < 1 or upload_size_in_mb > 4096:
            raise ValueError("uploadSize must be between 1 MB and 4096 MB. This is a limitation of AWS Glacier.")
        self.upload_size = upload_size_in_mb
        super().__init__()

    def upload(self, data: Generator):
        region = read_settings("default", "region")
        vault = read_settings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        glacier_client = boto3.client('glacier', region_name=region)
        date:str = datetime.now().strftime("%Y-%m-%d")
        file_name:str = date + self.get_file_extension(self.service)

        upload_size_bytes = self.upload_size * 1024 * 1024

        if self.dryrun:
            print(f"DRY RUN: Uploading {file_name} to Glacier vault {vault} in {region} region with {upload_size_bytes} byte parts")
            creation_response = {
                'uploadId': 'DRY_RUN_UPLOAD_ID',
                'location': 'DRY_RUN_LOCATION'
            }
        else:
            try:
                creation_response = glacier_client.initiate_multipart_upload(
                    vaultName=vault,
                    archiveDescription=f'{file_name}',
                    partSize=str(upload_size_bytes)
                )
            except Exception as exception:
                print(exception)
                return False
        upload_id = creation_response['uploadId']
        location = creation_response['location']
        print(f"Glacier Upload ID: {upload_id} and location: {location}")

        upload_total_size_in_bytes = 0
        all_uploaded_parts = []
        all_checksums:list[str] = []
        creater = TransferServiceGlacierFileCreater()
        loop_index = 0
        while True:
            with tempfile.TemporaryFile(mode="b+w") as temp_file:
                try:
                    creater.create_next_upload_size_part(data, upload_size_bytes, temp_file)
                    chs = botocore.utils.calculate_tree_hash(temp_file)
                except StopIteration:
                    temp_file.close()
                    break
                temp_file.seek(0, 2)
                temp_file_size = temp_file.tell()
                temp_file.seek(0)

                if self.dryrun:
                    part_response = {
                        'checksum': 'DRY_RUN_CHECKSUM'
                    }
                else:
                    byte_range = f"bytes {loop_index * upload_size_bytes}-{(loop_index * upload_size_bytes) + temp_file_size - 1}/*"
                    try:
                        part_response = glacier_client.upload_multipart_part(
                            vaultName=vault,
                            uploadId=upload_id,
                            body=temp_file,
                            range=byte_range,
                            checksum=chs
                        )
                    except Exception as exception:
                        print("Error during a part upload.")
                        print(exception)
                        # TODO: retry Upload
                        return False

                upload_total_size_in_bytes += temp_file_size
                print(f"Uploaded part {loop_index} with size: {temp_file_size} bytes")
                print(f"Part response: {part_response}")
                all_checksums.append(chs)
                print(f"checksum from method:   {chs}")
                print(f"checksum from response: {str(part_response['checksum'])}")
                # all_checksums.append(str(part_response['checksum']))
                all_uploaded_parts.append({
                    'PartNumber': loop_index,
                    'ETag': part_response['checksum']
                })

            loop_index += 1
        print(f"Total Written bytes: {creater.total_written_bytes}")
        print(f"Total Read bytes: {creater.total_read_bytes}")
        print(f"Total remaining bytes: {len(creater.remaining_bytes_from_last_part)}")
        print(f"Total size: {upload_total_size_in_bytes} bytes after function")

        checksum = compute_sha256_tree_hash(all_checksums)
        print(f"Checksum: {checksum}")

        if checksum == "" or checksum is None:
            print("Error calculating checksum. Upload cannot be completed")
            return False
        try:
            if self.dryrun:
                complete_status = {
                    'archiveId': 'DRY_RUN_ARCHIVE_ID',
                    'checksum': checksum
                }
            else:
                complete_status = glacier_client.complete_multipart_upload(
                    vaultName=vault,
                    uploadId=upload_id,
                    archiveSize=str(upload_total_size_in_bytes),
                    checksum=checksum
                )
            print(f"Upload complete. Archive ID: {complete_status['archiveId']}, Checksum: {complete_status['checksum']}")
            return True
        except Exception as exception:
            print("Error completing upload")
            print(exception)
            return False

    def download(self, data: Generator):
        return data
