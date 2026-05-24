import logging
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status, Request
import os
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController


from models import ProjectModel, ResponseSignal, ChunkModel
from models.db_schemes.data_chunk import DataChunk
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
        print("project_model",project_model)

        project = await project_model.get_project_or_create_one(project_id)
        print("project",project)
         
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
        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
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
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    chunk_model = await ChunkModel.create_instance(req.app.db)
    project_model = await ProjectModel.create_instance(req.app.db) 


    process_controller = ProcessController(project_id)
    file_content = process_controller.get_file_content(file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content, chunk_size=chunk_size, overlap_size=overlap_size
    )
    
    project = await project_model.get_project_or_create_one(project_id)
    if file_chunks is None:
        return JSONResponse(
            content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    file_chunks_records =[
        DataChunk(
            text=chunk.page_content,
            metadata=chunk.metadata,
            order=index + 1,
            project_id=project.id
        )
        for index, chunk in enumerate(file_chunks)
    ]    

    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project.id)
   
    inserted_count = await chunk_model.insert_many_chunks(file_chunks_records)
    if inserted_count != len(file_chunks_records):
        return JSONResponse(
            content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        content={"signal": ResponseSignal.PROCESSING_SUCCESS.value ,"inserted_chunks":inserted_count},
        status_code=status.HTTP_200_OK,
         
    )
