import os

def store_aws_credentials(access_key, secret_key, profile_name='default'):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    aws_dir = os.path.join(home, '.aws')
    if not os.path.exists(aws_dir):
        os.makedirs(aws_dir)

    # Path to the credentials file
    credentials_file = os.path.join(aws_dir, 'credentials')

    # Write the credentials
    with open(credentials_file, 'w', encoding='utf-8') as file:
        file.write(f'[{profile_name}]\n')
        file.write(f'aws_access_key_id = {access_key}\n')
        file.write(f'aws_secret_access_key = {secret_key}\n')

def check_aws_credentials(profile_name='default'):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    aws_dir = os.path.join(home, '.aws')
    if not os.path.exists(aws_dir):
        os.makedirs(aws_dir)

    # Path to the credentials file
    credentials_file = os.path.join(aws_dir, 'credentials')

    # Write the credentials
    with open(credentials_file, 'r', encoding='utf-8') as file:
        credentials_data = file.read()
        return bool(profile_name in credentials_data)
