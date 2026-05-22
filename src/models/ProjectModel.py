


from pymongo import MongoClient
from helpers.config import get_settings
from .BaseDataModel import BaseDataModel 
from models.db_schemes.project import Project
from models.enums import DataBaseEnum


class ProjectModel(BaseDataModel):
    def  __init__(self,db_client:MongoClient):
        super().__init__(db_client)
        self.collection=db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]


    async def create_project(self,project:Project):
        result= await self.collection.insert_one(project.model_dump())
        return result.inserted_id

    async def  get_project_or_create_one(self,project_id:str):
        result= await self.collection.find_one({"project_id":project_id})
        if result:
            return Project(**result)
        else:
            return await self.create_project(Project(project_id=project_id))

    async def get_all_projects(self,page:int=1,page_size:int=10):
        
        total_documents= await self.collection.count_documents({})
        total_pages= total_documents//page_size
        result= await self.collection.find().skip((page-1)*page_size).limit(page_size).to_list(length=None)
        return {
            "data": [Project(**result) for result in result],
            "total_pages": total_pages,
            "total_documents": total_documents,
            "page": page,
            "page_size": page_size
        }

    async def get_project(self,project_id:str):
        result= await self.collection.find_one({"_id":project_id})
        return Project(**result)

    async def update_project(self,project_id:str,project:Project):
        result= await self.collection.update_one({"_id":project_id},{"$set":project.model_dump()})
        return result.modified_count
    
    async def delete_project(self,project_id:str):
        result= await self.collection.delete_one({"_id":project_id})
        return result.deleted_count