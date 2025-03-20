from helpers.config import get_settings, Settings
import os
import random
import string


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, 'assets/files')
        self.database_dir = os.path.join(self.base_dir, 'assets/database')

    def generate_random_strings(self, length: int = 12):
        return ''.join(random.choices(string.ascii_lowercase+string.digits, k=length))

    def get_db_path(self, db_name: str):
        db_path = os.path.join(self.database_dir, db_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        return db_path
