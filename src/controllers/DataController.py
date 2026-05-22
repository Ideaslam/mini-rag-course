import os
import re
from .ProjectController import ProjectController
from .BaseController import BaseController
from fastapi import UploadFile,Depends
from models import ResponseSignal

class DataController(BaseController):
     
    def __init__(self,project_controller:ProjectController=Depends(ProjectController)):
        super().__init__()
        self.size_scale= 1024 *1024 # 1MB
        self.project_controller = project_controller

    def validate_uploaded_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size    > self.app_settings.FILE_MAX_SIZE *  self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value    

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filename(self,origin_filename:str,project_id:str):
        random_key = self.generate_random_string()
        project_dir = self.project_controller.get_project_path(project_id)
        clean_filename = self.get_clean_file_name(origin_filename)
        new_file_path = os.path.join(project_dir,f"{random_key}_{clean_filename}")
        if os.path.exists(new_file_path):
            return self.generate_unique_filename(origin_filename,project_id)
        return new_file_path

    def get_clean_file_name(self,origin_filename:str):
        cleaned_file_name=re.sub(r'[^\w.]', '_', origin_filename.strip())    
        cleaned_file_name=cleaned_file_name.replace(" ","_")
        return cleaned_file_name