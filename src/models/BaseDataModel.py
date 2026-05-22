

from pymongo import MongoClient

from helpers.config import get_settings


class BaseDataModel:
    def  __init__(self,db_client:MongoClient):
        self.db_client = db_client
        self.app_settings = get_settings()