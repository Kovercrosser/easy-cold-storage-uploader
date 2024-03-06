import re
import boto3

from utils.storageUtils import storeSettings
from utils.awsUtils import storeAwsCredentials, checkAwsCredentials
from utils.consoleUtils import clearConsole, forceUserInputFromList, forceUserInput

def chooseRegion():
    session = boto3.Session()
    glacierRegions = session.get_available_regions('glacier')
    result = forceUserInputFromList("Glacier Regions", glacierRegions)
    return glacierRegions[result - 1]

def chooseVault(region):
    index = forceUserInputFromList("Choose an existing Vault or create a new one:", ["Create new Vault", "Choose existing Vault"])
    choosenVault = ""
    if index == 1:
        choosenVault = createVault(region)
    if index == 2:
        vaults = getAllVaults(region)
        vaultNameList = [vault['VaultName'] for vault in vaults]
        result = forceUserInputFromList("Choose your Vault:", vaultNameList)
        choosenVault = vaultNameList[result - 1]
    return choosenVault

def enterApiKeys():
    print("Warning: Your API Key and API Secret Key will be stored in plain text in a local file under ~/.aws/credentials.")
    apiKey = forceUserInput("Enter your API Key:")
    apiSecretKey = forceUserInput("Enter your API Secret Key:")
    storeAwsCredentials(apiKey, apiSecretKey)

def getAllVaults(region):
    glacierClient = boto3.client('glacier', region_name=region)
    response = glacierClient.list_vaults()
    vaults = response['VaultList']
    return vaults

def createVault(region):
    vaults = getAllVaults(region)
    print("Enter the name of the new Vault:")
    while True:
        vaultName = input()
        if not re.match(r"^[a-zA-Z0-9-_]+$", vaultName):
            print("Invalid vault name. Please use only alphanumeric characters, hyphens, and underscores.")
        elif vaultName in [vault['VaultName'] for vault in vaults]:
            print("Vault already exists. Please choose another name.")
        else:
            break
    print(f"\nYou chose {vaultName} as the name of your new Vault.")
    glacierClient = boto3.client('glacier', region_name=region)
    glacierClient.create_vault(vaultName=vaultName)
    print(f"Vault {vaultName} has been created.")
    input("Press Enter to continue...")
    return vaultName

def chooseCompression():
    compressionTypeList = ["None", "lzma", "bzip2"]
    compressionTypeListWithDescription = ["None", "lzma   (default)", "bzip2  (higher compression -> smaller Filesize, slower)"]
    result = forceUserInputFromList("Choose your Compression:", compressionTypeListWithDescription)
    return compressionTypeList[result - 1]

def chooseFileType():
    fileTypeList = ["None", "tar", "zip"]
    fileTypeListWithDescription = ["None  (Stores Files as they are)", "tar   (recommended)", "zip"]
    result = forceUserInputFromList("Choose your File Type:", fileTypeListWithDescription)
    return fileTypeList[result - 1]

def chooseEncryption():
    encryptionList = ["None", "aes", "rsa"]
    encryptionListWithDescription = ["None  (Stores Files unencrypted)", "AES   (recommended)", "RSA"]
    result = forceUserInputFromList("Choose your Encryption:", encryptionListWithDescription)
    return encryptionList[result - 1]

def setup():
    clearConsole("Setup Glacier Backup")

    if checkAwsCredentials():
        print("You already have AWS Credentials stored in ~/.aws/credentials.")
        result = forceUserInput("Do you want to overwrite them? y/n", ["y", "n"])
        if result == "y":
            enterApiKeys()
            clearConsole("Setup Glacier Backup")
            print("Your Credentials have been stored in the file ~/.aws/credentials")
        else:
            clearConsole("Setup Glacier Backup")
    else:
        enterApiKeys()
        clearConsole("Setup Glacier Backup")
        print("Your Credentials have been stored in the file ~/.aws/credentials")

    region = chooseRegion()
    clearConsole("Setup Glacier Backup")
    print(f"\nYou chose {region} as your Glacier Region.\n")

    choosenVault = chooseVault(region)
    clearConsole("Setup Glacier Backup")
    print(f"\nYou chose {choosenVault} as your Vault.\n")

    choosenCompression = chooseCompression()
    clearConsole("Setup Glacier Backup")
    print(f"\nYou chose {choosenCompression} as your Compression Method.")

    choosenFileType = chooseFileType()
    clearConsole("Setup Glacier Backup")
    print(f"\nYou chose {choosenFileType} as your File Type.")

    choosenEncryption = chooseEncryption()
    clearConsole("Setup Glacier Backup")
    print(f"\nYou chose {choosenEncryption} as your Encryption.")

    storeSettings("default", "region", region)
    storeSettings("default", "vault", choosenVault)
    storeSettings("default", "compression", choosenCompression)
    storeSettings("default", "filetype", choosenFileType)
    storeSettings("default", "encryption", choosenEncryption)
    storeSettings("global", "setup", True)
    print("Your Configuration has been stored in the file ~/.glacier-backup/settings")
    print("Setup complete.")
    input("Press Enter to continue...")
