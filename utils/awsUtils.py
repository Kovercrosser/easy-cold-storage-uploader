import os

def storeAwsCredentials(accessKey, secretKey, profileName='default'):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    awsDir = os.path.join(home, '.aws')
    if not os.path.exists(awsDir):
        os.makedirs(awsDir)

    # Path to the credentials file
    credentialsFile = os.path.join(awsDir, 'credentials')

    # Write the credentials
    with open(credentialsFile, 'w', encoding='utf-8') as file:
        file.write(f'[{profileName}]\n')
        file.write(f'aws_access_key_id = {accessKey}\n')
        file.write(f'aws_secret_access_key = {secretKey}\n')

def checkAwsCredentials(profileName='default'):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    awsDir = os.path.join(home, '.aws')
    if not os.path.exists(awsDir):
        os.makedirs(awsDir)

    # Path to the credentials file
    credentialsFile = os.path.join(awsDir, 'credentials')

    # Write the credentials
    with open(credentialsFile, 'r', encoding='utf-8') as file:
        credentialsData = file.read()
        return bool(profileName in credentialsData)
