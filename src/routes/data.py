from datetime import datetime, timezone
import logging
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status, Request
import os
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController


from models import AssetModel, ProjectModel, ResponseSignal, ChunkModel
from models.db_schemes.asset import Asset
from models.db_schemes.data_chunk import DataChunk
from models.enums import AssetTypeEnum
from .schemas import ProcessRequest


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    data_controller: DataController = Depends(DataController),
):
    try:

        project_model = await ProjectModel.create_instance(request.app.db)
     

        project = await project_model.get_project_or_create_one(project_id)
       
         
        is_valid, message = data_controller.validate_uploaded_file(file)
        if not is_valid:
            return JSONResponse(
                content={"signal": message}, status_code=status.HTTP_400_BAD_REQUEST
            )

        file_path, file_id = data_controller.generate_unique_filepath(
            file.filename, project_id
        )
        async with aiofiles.open(file_path, mode="wb") as f:
            while chunk := await file.read(
                data_controller.app_settings.FILE_DEFAULT_CHUNK_SIZE
            ):
                await f.write(chunk)


        asset_model = await AssetModel.create_instance(request.app.db)
        asset = Asset(
            project_id=project.id,
            name=file_id,
            size=os.path.getsize(file_path),
            type=AssetTypeEnum.FILE.value,
            config={},
            pushed_at=datetime.now(timezone.utc)
        )
        asset_result = await asset_model.create_asset(asset)


        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id":str(asset_result.id)
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"FILE_UPLOAD_ERROR: {str(e)}")
        return JSONResponse(
            content={"signal": f"FILE_UPLOAD_ERROR: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(req: Request, project_id: str, process_request: ProcessRequest):
    
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    chunk_model = await ChunkModel.create_instance(req.app.db)
    project_model = await ProjectModel.create_instance(req.app.db) 

    project = await project_model.get_project_or_create_one(project_id)
    

    asset_model = await AssetModel.create_instance(req.app.db)
    project_files_ids ={}
    if process_request.file_id is not None:
        asset = await asset_model.get_asset_record(project.id, process_request.file_id)
        if asset is None:
            return JSONResponse(
                content={"signal": ResponseSignal.FILE_ID_ERROR.value},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        project_files_ids ={
            asset.id:asset.name
        }
    else:
        
        project_files = await asset_model.get_all_project_assets(project.id, AssetTypeEnum.FILE.value)
        project_files_ids = {
            record.id:record.name
            for record in project_files
        }

    if len(project_files_ids) == 0:
        return JSONResponse(
            content={"signal": ResponseSignal.NO_FILES_FOUND.value},
            status_code=status.HTTP_404_NOT_FOUND,
        )


     
     

    process_controller = ProcessController(project_id)

    if do_reset == 1:
            await chunk_model.delete_chunks_by_project_id(project.id)

    no_records = 0
    no_files = 0
    for asset_id, file_id in project_files_ids.items():
       
        file_content = process_controller.get_file_content(file_id) 

        if file_content is None:
            logger.error(f"FILE_CONTENT_NOT_FOUND: {file_id}")
            continue
     
        file_chunks = process_controller.process_file_content(
            file_content=file_content, chunk_size=chunk_size, overlap_size=overlap_size
        )

        if file_chunks is None:
            continue

         
    
        file_chunks_records =[
            DataChunk(
                text=chunk.page_content,
                metadata=chunk.metadata,
                order=index + 1,
                project_id=project.id,
                asset_id=asset_id
            )
            for index, chunk in enumerate(file_chunks)
        ]    

        
    
        no_records += await chunk_model.insert_many_chunks(file_chunks_records)
        no_files += 1
        # if no_records != len(file_chunks_records):
        #     return JSONResponse(
        #         content={"signal": ResponseSignal.PROCESSING_FAILED.value},
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )
    
    return JSONResponse(
        content={"signal": ResponseSignal.PROCESSING_SUCCESS.value ,"inserted_chunks":no_records,"no_files":no_files},
        status_code=status.HTTP_200_OK,
         
    )
