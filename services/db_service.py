import os
from tinydb import TinyDB


class DbService:
    db: TinyDB
    def __init__(self, db_name: str) -> None:
        if not db_name.endswith(".json"):
            raise ValueError("db_file must end with .json.")
        if len(db_name) < 5:
            raise ValueError("db_file must be at least 1 characters long and include '.json' at the end.")
        home = os.path.expanduser("~")
        ecsu_dir = os.path.join(home, '.ecsu')
        if not os.path.exists(ecsu_dir):
            os.makedirs(ecsu_dir)
        db_file_path = os.path.join(ecsu_dir, db_name)
        self.db = TinyDB(db_file_path)

    def get_context(self) -> TinyDB:
        return self.db
