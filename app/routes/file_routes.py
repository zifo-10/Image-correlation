import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File

from app.container import get_file_service
from app.exceptions.custom_exception import CustomHTTPException, CustomException
from app.service.file_service import FileService

router = APIRouter(prefix="/file", tags=["users"])


@router.post("")
async def create_user(service: FileService = Depends(get_file_service)):
    try:
        user_id = await service.create_file()
        return {"user_id": user_id}
    except CustomException as e:
        raise CustomHTTPException(status_code=e.status_code, detail=e.detail,
                                  exception_type=e.exception_type, additional_info=e.additional_info)


@router.post("/extract-image")
async def process_file(
        uploaded_file: UploadFile = File(...),
        service: FileService = Depends(get_file_service),
):
    try:
        # Read file bytes
        file_bytes = await uploaded_file.read()
        # Get original extension
        _, ext = os.path.splitext(uploaded_file.filename)
        # Generate unique file name
        # Upload to storage
        files = service.save_images_from_pdf(file_bytes)
        return {"status": "success", "data": files}
    except CustomException as e:
        raise CustomHTTPException(
            status_code=e.status_code,
            detail=e.detail,
            exception_type=e.exception_type,
            additional_info=e.additional_info,
        )


@router.post("/process-file")
async def extract_images_endpoint(
        pdf_file: UploadFile = File(...),
        service: FileService = Depends(get_file_service),
):
    """
    Upload a PDF, extract images, save file & image records,
    and upload images to storage.
    """
    try:
        pdf_bytes = await pdf_file.read()
        result = await service.process_file(
            pdf_bytes, filename=pdf_file.filename
        )
        return {"status": "success", "data": result}
    except CustomException as e:
        raise CustomHTTPException(
            status_code=e.status_code,
            detail=e.detail,
            exception_type=e.exception_type,
            additional_info=e.additional_info,
        )


@router.post("/describe-image")
async def describe_image(file: UploadFile = File(...),
                         service: FileService = Depends(get_file_service)):
    try:
        image_bytes = await file.read()

        result = await service.image_description(
            image_bytes=image_bytes,
        )
        return result
    except Exception as e:
        raise CustomHTTPException(status_code=500, detail="Internal Server Error",
                                  exception_type="InternalServerError", additional_info={"error": str(e)})
