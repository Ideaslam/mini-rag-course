
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field,field_validator
from datetime import datetime, timezone


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: ObjectId
    type: str = Field(...,min_length=1)
    name : str = Field(...,min_length=1)
    size: int = Field(...,ge=0)
    config : dict = Field(default={})
    pushed_at : datetime = Field(default=datetime.now(timezone.utc))
    


    class Config:
        arbitrary_types_allowed = True


    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", 1),
                ],
                "name": "idx_project_id",
                "unique": False,
            },
              {
                "key": [
                    ("name", 1),
                    ("project_id", 1),
                ],
                "name": "idx_name_project_id",
                "unique": True,
            }

        ]