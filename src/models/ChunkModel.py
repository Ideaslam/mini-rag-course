from bson.objectid import ObjectId
from pymongo import InsertOne
from pymongo.asynchronous.database import AsyncDatabase

from .db_schemes.data_chunk import DataChunk

from .db_schemes.project import Project

from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum


class ChunkModel(BaseDataModel):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db)
        self.collection = db[DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value]

    @classmethod
    async def create_instance(cls, db: AsyncDatabase):
        instance = cls(db)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        indexes = DataChunk.get_indexes()
        for index in indexes:
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.model_dump(exclude_none=True))
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if result:
            return DataChunk(**result)
        return None

    async def get_all_chunks(self, page: int = 1, page_size: int = 10):
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size


    async def insert_many_chunks(self, chunks: list,batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations = [
                InsertOne(
                    document=chunk.model_dump(exclude_none=True),
                )
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)


    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count