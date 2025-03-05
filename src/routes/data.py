from fastapi import APIRouter,Depends,UploadFile,status,Request
from models.enums.ResponseEnums import ResponseSignals
from fastapi.responses import JSONResponse
from helpers.config import get_settings ,Settings
from controllers import DataController,ProcessController
from controllers import  ProjectControllers
from models.projectmodel import ProjectModel
from .schemas.data import ProcessRequest
from models.chunkModel import ChunkModel
from models.db_schemas import DataChunk
import  aiofiles
import logging
logger=logging.getLogger('uvicorn.error')
data_router=APIRouter(
    prefix='/api/v1/data',
    tags=["api_v1","data"]
)

@data_router.post('/upload/{proj_id}')
async def upload_data(request:Request,proj_id:str,file:UploadFile,
                      app_settings=Depends(get_settings)):


    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.getproject_createone(proj_id)

# validate the file
    is_valid,signal=DataController().validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":signal
            }
        )
    project_dir_path=ProjectControllers().get_proj_path(proj_id)
    file_path,file_uniqueid=DataController().generate_filenames(orig_name=file.filename,proj_id=proj_id)
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"While Uploading File: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "Error In Uploading Please Contact Support"
            }
        )

    return JSONResponse(

                    content={
                      "signal":ResponseSignals.FILE_UPLOADED_SUCCESSFULLY.value
                    ,"fileid":file_uniqueid
         }
)


@data_router.post('/process/{proj_id}')

async def process_endpoint(request:Request,proj_id:str,req:ProcessRequest):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.getproject_createone(proj_id)
    file_id=req.file_id
    do_reset=req.do_reset
    process_controller=ProcessController(proj_id)
    file_content=process_controller.get_content(file_id)
    file_chunks=process_controller.process_file_content(file_content,file_id)
    if file_chunks is None or len(file_chunks)==0:
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal":ResponseSignals.PROCESSING_FAILED
        }
    chunk_model=await ChunkModel.create_instance(
        db_client=request.app.db_client
    )
    if do_reset == 1:
      await  chunk_model.delete_chunk_byprojid(project.id)

    file_chunks_records=[
        DataChunk(

    chunk_text=chunk.page_content,
    chunk_metadata=chunk.metadata,
    chunk_order=i+1,
    chunk_project_id=project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]
    no_records=await chunk_model.insert_many_chunks(file_chunks_records)
    return JSONResponse( content=
    {
       "signal":ResponseSignals.PROCESSING_SUCESS.value,
        "inserted_chunks":no_records
    })