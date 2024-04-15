import re
import boto3

from utils.storage_utils import store_settings
from utils.aws_utils import store_aws_credentials, check_aws_credentials
from utils.console_utils import clear_console, force_user_input_from_list, force_user_input

def choose_region() -> str:
    session = boto3.Session()
    glacier_regions = session.get_available_regions('glacier')
    result = force_user_input_from_list("Glacier Regions", glacier_regions)
    return glacier_regions[result - 1]

def choose_vault(region: str) -> str:
    index = force_user_input_from_list("Choose an existing Vault or create a new one:", ["Create new Vault", "Choose existing Vault"])
    choosen_vault = ""
    if index == 1:
        choosen_vault = create_vault(region)
    if index == 2:
        vault_name_list = get_all_vault_names(region)
        result = force_user_input_from_list("Choose your Vault:", vault_name_list)
        choosen_vault = vault_name_list[result - 1]
    return choosen_vault

def enter_api_keys() -> None:
    print("Warning: Your API Key and API Secret Key will be stored in plain text in a local file under ~/.aws/credentials.")
    api_key = force_user_input("Enter your API Key:", None)
    api_secret_key = force_user_input("Enter your API Secret Key:", None)
    store_aws_credentials(api_key, api_secret_key)

def get_all_vault_names(region: str) -> list[str]:
    glacier_client = boto3.client('glacier', region_name=region)
    response = glacier_client.list_vaults()
    vaults_response = response['VaultList']
    if isinstance(vaults_response, list) and len(vaults_response) > 0:
        if all(isinstance(vault, dict) for vault in vaults_response) and all('VaultName' in vault for vault in vaults_response):
            return [vault['VaultName'] for vault in vaults_response]
    return []

def create_vault(region: str) -> str:
    vaults = get_all_vault_names(region)
    print("Enter the name of the new Vault:")
    while True:
        vault_name = input()
        if not re.match(r"^[a-zA-Z0-9-_]+$", vault_name):
            print("Invalid vault name. Please use only alphanumeric characters, hyphens, and underscores.")
        elif vault_name in vaults:
            print("Vault already exists. Please choose another name.")
        else:
            break
    print(f"\nYou chose {vault_name} as the name of your new Vault.")
    glacier_client = boto3.client('glacier', region_name=region)
    glacier_client.create_vault(vaultName=vault_name)
    print(f"Vault {vault_name} has been created.")
    input("Press Enter to continue...")
    return vault_name

def choose_compression() -> str:
    compression_type_list = ["None", "lzma", "bzip2"]
    compression_type_list_with_description = ["None", "lzma   (default)", "bzip2  (higher compression -> smaller Filesize, slower)"]
    result = force_user_input_from_list("Choose your Compression:", compression_type_list_with_description)
    return compression_type_list[result - 1]

def choose_file_type() -> str:
    file_type_list = ["None", "tar", "zip"]
    file_type_list_with_description = ["None  (Stores Files as they are)", "tar   (recommended)", "zip"]
    result = force_user_input_from_list("Choose your File Type:", file_type_list_with_description)
    return file_type_list[result - 1]

def choose_encryption() -> str:
    encryption_list = ["None", "aes", "rsa"]
    encryption_list_with_description = ["None  (Stores Files unencrypted)", "AES   (recommended)", "RSA"]
    result = force_user_input_from_list("Choose your Encryption:", encryption_list_with_description)
    return encryption_list[result - 1]

def setup() -> None:
    clear_console("Setup Glacier Backup")

    if check_aws_credentials():
        print("You already have AWS Credentials stored in ~/.aws/credentials.")
        result = force_user_input("Do you want to overwrite them? y/n", ["y", "n"])
        if result == "y":
            enter_api_keys()
            clear_console("Setup Glacier Backup")
            print("Your Credentials have been stored in the file ~/.aws/credentials")
        else:
            clear_console("Setup Glacier Backup")
    else:
        enter_api_keys()
        clear_console("Setup Glacier Backup")
        print("Your Credentials have been stored in the file ~/.aws/credentials")

    region = choose_region()
    clear_console("Setup Glacier Backup")
    print(f"\nYou chose {region} as your Glacier Region.\n")

    choosen_vault = choose_vault(region)
    clear_console("Setup Glacier Backup")
    print(f"\nYou chose {choosen_vault} as your Vault.\n")

    choosen_compression = choose_compression()
    clear_console("Setup Glacier Backup")
    print(f"\nYou chose {choosen_compression} as your Compression Method.")

    choosen_file_type = choose_file_type()
    clear_console("Setup Glacier Backup")
    print(f"\nYou chose {choosen_file_type} as your File Type.")

    choosen_encryption = choose_encryption()
    clear_console("Setup Glacier Backup")
    print(f"\nYou chose {choosen_encryption} as your Encryption.")

    store_settings("default", "region", region)
    store_settings("default", "vault", choosen_vault)
    store_settings("default", "compression", choosen_compression)
    store_settings("default", "filetype", choosen_file_type)
    store_settings("default", "encryption", choosen_encryption)
    store_settings("global", "setup", "True")
    print("Your Configuration has been stored in the file ~/.glacier-backup/settings")
    print("Setup complete.")
    input("Press Enter to continue...")
