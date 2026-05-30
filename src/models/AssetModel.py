from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from .db_schemes.asset import Asset

from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db)
        self.collection = db[DataBaseEnum.COLLECTION_ASSETS_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncMongoClient):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        indexes = Asset.get_indexes()
        for index in indexes:
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.model_dump(exclude_none=True))
        asset.id=result.inserted_id
        return asset

    async def get_asset_by_name_and_project(self, name: str, project_id: ObjectId):
        result = await self.collection.find_one({"name": name, "project_id": project_id})
        print("result get_asset_by_name_and_project", result)
        if result:
            return Asset(**result)
        return None

    async def get_all_assets(self, page: int = 1, page_size: int = 10, project_id: ObjectId = None):
        query = {}
        if project_id is not None:
            query["project_id"] = project_id

        total_documents = await self.collection.count_documents(query)
        total_pages = total_documents // page_size
        result = (
            await self.collection.find(query)
            .skip((page - 1) * page_size)
            .limit(page_size)
            .to_list(length=None)
        )
        return {
            "data": [Asset(**doc) for doc in result],
            "total_pages": total_pages,
            "total_documents": total_documents,
            "page": page,
            "page_size": page_size,
        }

    async def get_all_project_assets(self, project_id: str,type:str):
        result=   await self.collection.find(
        {"project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id,
         "type": type
        }).to_list(length=None)

        return [Asset(**record) for record in result]



    async def get_asset(self, asset_id: str):
        result = await self.collection.find_one({"_id": ObjectId(asset_id)})
        if result:
            return Asset(**result)
        return None

    async def get_asset_record(self, project_id: str, name: str):
        result = await self.collection.find_one({"project_id": ObjectId(project_id), "name": name})
        if result:
            return Asset(**result)
        return None

    async def update_asset(self, asset_id: str, asset: Asset):
        result = await self.collection.update_one(
            {"_id": ObjectId(asset_id)},
            {"$set": asset.model_dump(exclude_none=True)},
        )
        return result.modified_count

    async def delete_asset(self, asset_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(asset_id)})
        return result.deleted_count

    async def delete_assets_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count
