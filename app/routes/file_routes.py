import os

from fastapi import APIRouter, Depends, UploadFile, File, Query
from tavily import TavilyClient

from app.config import settings
from app.container import get_file_service
from app.exceptions.custom_exception import CustomHTTPException, CustomException
from app.service.file_service import FileService

router = APIRouter(prefix="/file", tags=["File"])


@router.post("/extract-image")
async def extract_image(
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
async def process_file_pdf(
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


@router.get("/search-image")
async def search_image(
        query: str = Query(..., description="Search query"),
        top_n: int = Query(1, ge=1, le=10, description="Number of images to return"),
):
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(
            query=query,
            include_images=True,
            max_results=top_n,
        )

        images = response.get("images", [])

        return {"images": images[:top_n]}
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to fetch images",
            exception_type="TavilySearchError",
            additional_info={"error": str(e)},
        )
