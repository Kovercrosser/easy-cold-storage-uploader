from tinydb import TinyDB, where
from dependency_injection.service import Service
from services.db_service import DbService
from services.service_base import ServiceBase

class SettingService(ServiceBase):
    db: TinyDB
    def __init__(self, service: Service) -> None:
        db_service: DbService = service.get_service("settings_db_service")
        assert db_service is not None
        self.db = db_service.get_context()

    def store_settings(self, profile: str, key: str, value: str) -> None:
        profiles_table = self.db.table("profiles")
        profiles_table.upsert({"profile": profile, "key": key, "value": value}, (where('profile') == profile) & (where('key') == key))

    def read_settings(self, profile: str, key: str) -> str | None:
        profiles_table = self.db.table("profiles")
        result = profiles_table.get((where('profile') == profile) & (where('key') == key))
        if isinstance(result, dict):
            return result.get('value')
        elif isinstance(result, list):
            if isinstance(result[0], dict):
                return result[0].get('value')
        return None
