import logging
import aiofiles
from fastapi import  APIRouter,Depends,UploadFile,status
import os
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from controllers import DataController ,ProjectController
 

from  models import ResponseSignal
 

logger= logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)
@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str,file:UploadFile,data_controller:DataController=Depends(DataController),project_controller:ProjectController=Depends(ProjectController)):
    try:
        is_valid, message = data_controller.validate_uploaded_file(file)
        if not is_valid:
            return JSONResponse(content={"signal": message}, status_code=status.HTTP_400_BAD_REQUEST)

        project_dir_path = project_controller.get_project_path(project_id)
        file_name=data_controller.generate_unique_filename(file.filename,project_id)
        file_path = os.path.join(project_dir_path, file_name)
        async with aiofiles.open(file_path, mode="wb") as f:
            while chunk := await file.read(data_controller.app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

        return JSONResponse(
            content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"FILE_UPLOAD_ERROR: {str(e)}")
        return JSONResponse(
            content={"signal": f"FILE_UPLOAD_ERROR: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )