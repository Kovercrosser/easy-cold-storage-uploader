import os
import json

def storeSettings(profile: str, key: str, value):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    glacierDir = os.path.join(home, '.glacier-backup')
    if not os.path.exists(glacierDir):
        os.makedirs(glacierDir)

    # Path to the settings file
    settingsFile = os.path.join(glacierDir, 'settings')
    if not os.path.exists(settingsFile):
        with open(settingsFile, 'w', encoding='utf-8') as file:
            file.write('{}')

    settingsData = ""
    with open(settingsFile, 'r', encoding='utf-8') as file:
        settingsData = file.read()

    settingsJson = json.loads(settingsData) if settingsData else {}
    if profile not in settingsJson:
        settingsJson[profile] = {}
    settingsJson[profile][key] = value
    settingsData = json.dumps(settingsJson)

    with open(settingsFile, 'w', encoding='utf-8') as file:
        file.write(settingsData)

def readSettings(profile: str, key: str):
    # Determine the home directory
    home = os.path.expanduser("~")

    # Construct the .aws directory path
    glacierDir = os.path.join(home, '.glacier-backup')
    if not os.path.exists(glacierDir):
        os.makedirs(glacierDir)

    # Path to the settings file
    settingsFile = os.path.join(glacierDir, 'settings')
    if not os.path.isfile(settingsFile):
        return None
    try:
        with open(settingsFile, 'r', encoding='utf-8') as file:
            settingsData = file.read()
            settingsJson = json.loads(settingsData)
            return settingsJson[profile][key]
    except Exception:
        return None
