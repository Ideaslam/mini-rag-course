import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field,field_validator


class DataChunk(BaseModel):
    id:Optional[ObjectId] = Field(default=None, alias="_id")
    text  :str = Field(...,min_length=1)
    metadata: dict
    order: int = Field(...,ge=0)
    project_id:ObjectId

    class Config:
        arbitrary_types_allowed = True