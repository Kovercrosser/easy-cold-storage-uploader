import json
import os

from dependency_injection.service import Service
from services.db_service import DbService

class SettingService:
    db_service: DbService
    def __init__(self, service: Service) -> None:
        self.db_service = service.get_service("settings_db_service")

    def store_settings(self, profile: str, key: str, value: str) -> None:
        home = os.path.expanduser("~")
        ecsu_dir = os.path.join(home, '.ecsu')
        if not os.path.exists(ecsu_dir):
            os.makedirs(ecsu_dir)

        # Path to the settings file
        settings_file = os.path.join(ecsu_dir, 'settings.json')
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

    def read_settings(self, profile: str, key: str) -> str | None:
        home = os.path.expanduser("~")
        ecsu_dir = os.path.join(home, '.ecsu')
        if not os.path.exists(ecsu_dir):
            os.makedirs(ecsu_dir)

        # Path to the settings file
        settings_file = os.path.join(ecsu_dir, 'settings.json')
        if not os.path.isfile(settings_file):
            return None
        try:
            with open(settings_file, 'r', encoding='utf-8') as file:
                settings_data = file.read()
                settings_json = json.loads(settings_data)
                return str(settings_json[profile][key])
        except Exception:
            return None
