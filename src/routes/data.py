from fastapi import APIRouter, File, HTTPException, UploadFile

from controllers.DataController import DataController
from routes.schema.data import RequestProcess

router = APIRouter(prefix="/api/data", tags=["data"])

data_controller = DataController()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
  try:
    return await data_controller.save_upload(file)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))


@router.post("/process")
def process_data(request: RequestProcess):
  try:
    return data_controller.process_files(
        request.chunk_size,
        request.overlap,
        request.do_reset
    )
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))
