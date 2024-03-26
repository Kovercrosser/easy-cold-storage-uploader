import os
import json

def get_all_files_from_directories_and_files(paths: list[str]) -> list[str]:
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        else:
            for root, _, all_files in os.walk(path):
                for file in all_files:
                    file_path = os.path.join(root, file)
                    files.append(file_path)
    return files

def store_settings(profile: str, key: str, value):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    glacier_dir = os.path.join(home, '.glacier-backup')
    if not os.path.exists(glacier_dir):
        os.makedirs(glacier_dir)

    # Path to the settings file
    settings_file = os.path.join(glacier_dir, 'settings')
    if not os.path.exists(settings_file):
        with open(settings_file, 'w', encoding='utf-8') as file:
            file.write('{}')

    settings_data = ""
    with open(settings_file, 'r', encoding='utf-8') as file:
        settings_data = file.read()

    settings_json = json.loads(settings_data) if settings_data else {}
    if profile not in settings_json:
        settings_json[profile] = {}
    settings_json[profile][key] = value
    settings_data = json.dumps(settings_json)

    with open(settings_file, 'w', encoding='utf-8') as file:
        file.write(settings_data)

def read_settings(profile: str, key: str):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    glacier_dir = os.path.join(home, '.glacier-backup')
    if not os.path.exists(glacier_dir):
        os.makedirs(glacier_dir)

    # Path to the settings file
    settings_file = os.path.join(glacier_dir, 'settings')
    if not os.path.isfile(settings_file):
        return None
    try:
        with open(settings_file, 'r', encoding='utf-8') as file:
            settings_data = file.read()
            settings_json = json.loads(settings_data)
            return settings_json[profile][key]
    except Exception:
        return None
