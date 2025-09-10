from typing import Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.database import Database
from app.client.openai_client import OpenAIClient
from app.client.storage import StorageClient
from app.config import settings
from app.repositories.file_repo import FileRepository
from app.repositories.image_repo import ImageRepository
from app.service.file_service import FileService

db = Database()


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    async for session in db.get_session():
        yield session

async def get_openai_client() -> AsyncGenerator[OpenAIClient, Any]:
    yield OpenAIClient(api_key=settings.OPENAI_API_KEY)

async def get_storage_client():
    yield StorageClient()


async def get_file_repository(
        session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[FileRepository, Any]:
    yield FileRepository(session)


async def get_image_repository(
        session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[ImageRepository, Any]:
    yield ImageRepository(session)


async def get_file_service(
        file_repo: FileRepository = Depends(get_file_repository),
        storage_client: StorageClient = Depends(get_storage_client),
        image_repo: ImageRepository = Depends(get_image_repository),
        openai_client: OpenAIClient = Depends(get_openai_client)
) -> AsyncGenerator["FileService", Any]:
    yield FileService(
        file_repo=file_repo,
        storage_service=storage_client,
        image_repo=image_repo,
        openai_client=openai_client,
        db=file_repo.db,
    )
