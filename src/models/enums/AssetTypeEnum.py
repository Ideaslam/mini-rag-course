

from enum import Enum


class AssetTypeEnum(Enum):
     FILE = "file"
     FOLDER = "folder"
     API = "api"
     OTHER = "other"
     UNKNOWN = "unknown"