import boto3
import re

from utils.storageUtils import storeSettings, readSettings


def upload(profile: str, paths: list) -> int:
    vault = readSettings(profile, "vault")

    # TODO: Implement upload logic
    print("Not implemented yet.")
    return -1
