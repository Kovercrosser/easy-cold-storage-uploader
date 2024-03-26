from datetime import datetime
from io import BufferedRandom
import tempfile
from typing import Generator
import boto3
from dependencyInjection.service import Service
from services.transfer.transferBase import TransferBase
from utils.hashUtils import computeSha256TtreeHash
from utils.storageUtils import readSettings

class TransferServiceGlacierFileCreater:
    remainingBytesFromLastPart: bytes = bytes()
    generatorExhausted: bool = False
    totalReadBytes: int = 0
    totalWrittenBytes: int = 0

    def createNextUploadSizePart(self, data: Generator, uploadSizeBytes: int, tempFile: BufferedRandom) -> BufferedRandom:
        currentWrittenBytes = 0

        if not tempFile:
            raise ValueError("tempFile is not set")
        if uploadSizeBytes <= 0:
            raise ValueError("uploadSizeBytes must be greater than 0")

        chunk: bytes = bytes()
        while True:
            try:
                chunk = next(data)
                self.totalReadBytes += len(chunk)
            except StopIteration as exception:
                self.generatorExhausted = True
                if self.remainingBytesFromLastPart == b"" and len(chunk) == 0:
                    raise exception

            if len(self.remainingBytesFromLastPart) > uploadSizeBytes:
                tempFile.write(self.remainingBytesFromLastPart[:uploadSizeBytes])
                currentWrittenBytes += uploadSizeBytes
                self.totalWrittenBytes += uploadSizeBytes
                self.remainingBytesFromLastPart = self.remainingBytesFromLastPart[uploadSizeBytes:]
                tempFile.seek(0)
                return tempFile

            # now self.remainingBytesFromLastPart is empty or smaller then uploadSizeBytes

            tempFile.write(self.remainingBytesFromLastPart)
            currentWrittenBytes += len(self.remainingBytesFromLastPart)
            self.totalWrittenBytes += len(self.remainingBytesFromLastPart)
            self.remainingBytesFromLastPart = bytes()
            maxWriteSizeAllowed = uploadSizeBytes - currentWrittenBytes

            if chunk:
                if len(chunk) > maxWriteSizeAllowed:
                    tempFile.write(chunk[:maxWriteSizeAllowed])
                    self.remainingBytesFromLastPart = chunk[maxWriteSizeAllowed:]
                    currentWrittenBytes += maxWriteSizeAllowed
                    self.totalWrittenBytes += maxWriteSizeAllowed
                    tempFile.seek(0)
                    return tempFile
                tempFile.write(chunk)
                currentWrittenBytes += len(chunk)
                self.totalWrittenBytes += len(chunk)

            if self.remainingBytesFromLastPart == b"" and self.generatorExhausted:
                tempFile.seek(0)
                return tempFile


class TransferServiceGlacier(TransferBase):
    service: Service
    uploadSize: int # in MB must be power of two e.g. 1, 2, 4, 8, 16, 32, 64, 128, 256, 512. Min 1MB, Max 4096MB
    dryRun: bool

    def __init__(self,  service: Service, dryRun: bool = False, uploadSizeMB: int = 16) -> None:
        self.service = service
        self.dryRun = dryRun
        if (uploadSizeMB & (uploadSizeMB - 1)) != 0:
            raise ValueError("uploadSize must be a power of 2. This is a limitation of AWS Glacier.")
        if uploadSizeMB <= 1 or uploadSizeMB >= 4096:
            raise ValueError("uploadSize must be between 1 MB and 4096 MB. This is a limitation of AWS Glacier.")
        self.uploadSize = uploadSizeMB
        super().__init__()

    def upload(self, data: Generator):
        region = readSettings("default", "region")
        vault = readSettings("default", "vault")
        if None in [region, vault]:
            raise Exception("Region or Vault is not set")
        glacierClient = boto3.client('glacier', region_name=region)
        date:str = datetime.now().strftime("%Y-%m-%d")
        fileName:str = date + self.getFileExtension(self.service)

        uploadSizeBytes = self.uploadSize * 1024 * 1024

        if self.dryRun:
            print(f"DRY RUN: Uploading {fileName} to Glacier vault {vault} in {region} region with {uploadSizeBytes} byte parts")
            creationResponse = {
                'uploadId': 'DRY_RUN_UPLOAD_ID',
                'location': 'DRY_RUN_LOCATION'
            }
        else:
            try:
                creationResponse = glacierClient.initiate_multipart_upload(
                    vaultName=vault,
                    archiveDescription=f'{fileName}',
                    partSize=str(uploadSizeBytes)
                )
            except Exception as exception:
                print(exception)
                return False
        uploadId = creationResponse['uploadId']
        location = creationResponse['location']
        print(f"Glacier Upload ID: {uploadId} and location: {location}")

        part = 0
        uploadTotalSizeInBytes = 0
        allUploadedParts = []
        allChecksums:list[str] = []
        creater = TransferServiceGlacierFileCreater()
        loopIndex = 0
        while True:
            with tempfile.TemporaryFile(mode="b+w") as tempFile:
                try:
                    creater.createNextUploadSizePart(data, uploadSizeBytes, tempFile)
                except StopIteration:
                    tempFile.close()
                    break
                tempFile.seek(0, 2)
                tempFileSize = tempFile.tell()
                tempFile.seek(0)
                try:
                    if self.dryRun:
                        partResponse = {
                            'checksum': 'DRY_RUN_CHECKSUM'
                        }
                    else:
                        partResponse = glacierClient.upload_multipart_part(
                            vaultName=vault,
                            uploadId=uploadId,
                            body=tempFile,
                            range=f"bytes {part * uploadSizeBytes}-{(part * uploadSizeBytes) + tempFileSize - 1}/*"
                        )
                    tempFile.close()
                except Exception as exception:
                    tempFile.close()
                    print("Error during a part upload.")
                    print(exception)
                    # TODO: retry Upload
                    return False
                uploadTotalSizeInBytes += tempFileSize
                print(f"Uploaded part {loopIndex} with size: {tempFileSize} bytes")
                print(f"Part response: {partResponse}")
                allChecksums.append(str(partResponse['checksum']))
                allUploadedParts.append({
                    'PartNumber': part,
                    'ETag': partResponse['checksum']
                })

            loopIndex += 1
        print(f"Total Written bytes: {creater.totalWrittenBytes}")
        print(f"Total Read bytes: {creater.totalReadBytes}")
        print(f"Total remaining bytes: {len(creater.remainingBytesFromLastPart)}")
        print(f"Total size: {uploadTotalSizeInBytes} bytes after function")

        checksum = computeSha256TtreeHash(allChecksums)
        print(f"Checksum: {checksum}")

        if checksum == "" or checksum is None:
            print("Error calculating checksum. Upload cannot be completed")
            return False
        try:
            if self.dryRun:
                completeStatus = {
                    'archiveId': 'DRY_RUN_ARCHIVE_ID',
                    'checksum': checksum
                }
            else:
                completeStatus = glacierClient.complete_multipart_upload(
                    vaultName=vault,
                    uploadId=uploadId,
                    archiveSize=str(uploadTotalSizeInBytes),
                    checksum=checksum
                )
            print(f"Upload complete. Archive ID: {completeStatus['archiveId']}, Checksum: {completeStatus['checksum']}")
            return True
        except Exception as exception:
            print("Error completing upload")
            print(exception)
            return False

    def download(self, data: Generator):
        return data
