

from pymongo.asynchronous.database import AsyncDatabase

from helpers.config import get_settings


class BaseDataModel:
    def __init__(self, db_client: AsyncDatabase):
        self.db_client = db_client
        self.app_settings = get_settings()