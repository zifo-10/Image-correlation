import os

import fitz

from app.client.openai_client import OpenAIClient
from app.client.storage import StorageClient
from app.exceptions.custom_exception import CustomException
from app.exceptions.service_exception import ServiceException
from app.repositories.file_repo import FileRepository
from app.repositories.image_repo import ImageRepository


class FileService:
    def __init__(
            self,
            db,
            file_repo: FileRepository,
            image_repo: ImageRepository,
            storage_service: StorageClient,
            openai_client: OpenAIClient,
    ):
        self.db = db
        self.file_repo = file_repo
        self.storage_service = storage_service
        self.image_repo = image_repo
        self.openai_client = openai_client

    import os

    def save_images_from_pdf(self, pdf_bytes: bytes, output_dir: str = "images") -> list[str]:
        """
        Extract images from a PDF given as bytes and save them locally.
        Returns a list of file paths where the images were saved.
        """
        saved_files = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Open PDF in memory
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_number in range(len(pdf_doc)):
            page = pdf_doc[page_number]
            images = page.get_images(full=True)

            for img_index, img in enumerate(images, start=1):
                xref = img[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                filename = f"page{page_number + 1}_img{img_index}.{image_ext}"

                file_path = os.path.join(output_dir, filename)

                # Save image to disk
                with open(file_path, "wb") as f:
                    f.write(image_bytes)

                saved_files.append(file_path)

        pdf_doc.close()
        return saved_files

    def extract_images_from_pdf(self, pdf_bytes: bytes):
        """
        Extract images from a PDF given as bytes.
        Returns a list of dicts: { 'image_bytes', 'filename', 'extension' }
        """
        images_list = []

        # Open PDF in memory
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_number in range(len(pdf_doc)):
            page = pdf_doc[page_number]
            images = page.get_images(full=True)

            for img_index, img in enumerate(images, start=1):
                xref = img[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                filename = f"page{page_number + 1}_img{img_index}.{image_ext}"

                images_list.append({
                    "image_bytes": image_bytes,
                    "filename": filename,
                    "extension": image_ext
                })

        pdf_doc.close()
        return images_list

    async def create_file(self):
        try:
            async with self.db.begin():
                file = await self.file_repo.create(
                    {
                        "file_name": "Test File",
                    }
                )
            return file.id
        except CustomException as e:
            raise e
        except Exception as e:
            raise ServiceException(
                status_code=500,
                detail="Failed to create user",
                additional_info={"error": str(e)},
            )

    async def upload_file_to_storage(self, file: bytes, file_name: str):
        try:
            file_url = self.storage_service.upload_file(
                bucket_name="files",
                file_name=file_name,
                content=file
            )
            return file_url

        except CustomException as e:
            raise e
        except Exception as e:
            raise ServiceException(
                status_code=500,
                detail="Failed to upload file to storage",
                additional_info={"error": str(e)},
            )

    async def process_file(self, file_bytes: bytes, filename: str, ) -> dict:
        try:
            print('Processing file:', filename)
            # 2️⃣ Insert PDF metadata in FileRepository
            file_record = await self.file_repo.create(
                {
                    "file_name": filename,
                }
            )
            print('File record created with ID:', file_record.id)

            # 3️⃣ Extract images from PDF
            images = self.extract_images_from_pdf(file_bytes)
            print('Images extracted from PDF:', len(images))
            for img in images:
                image_description = "description"
                image_type = "image"
                print("Uploading image:", img["filename"])
                # Insert image metadata in ImageRepository
                img_record = await self.image_repo.create(
                    {
                        "file_id": str(file_record.id),
                        "description": image_description,
                        "type": image_type
                    }
                )

                # Upload image to storage
                self.storage_service.upload_file(
                    bucket_name="files",
                    file_name=f"{str(file_record.id)}/{str(img_record.id)}",
                    content=img["image_bytes"]
                )
            return {"file_id": file_record.id, "image_count": len(images)}
        except CustomException as e:
            print(e)
            raise e

    async def image_description(self, image_bytes: bytes) -> dict:
        try:
            # Call OpenAI client to get image description
            description = self.openai_client.image_description(image_bytes=image_bytes)
            return {"description": description, "type": "image"}
        except CustomException as e:
            raise e
        except Exception as e:
            raise ServiceException(
                status_code=500,
                detail="Failed to get image description",
                additional_info={"error": str(e)},
            )
