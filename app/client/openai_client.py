import base64
import mimetypes
from typing import Optional, List, Literal

from openai import OpenAI
from openai.lib import ResponseFormatT
from pydantic import BaseModel
from app.constant_manager import image_description_prompt

# Structured response model
class ResponseModel(BaseModel):
    description: str
    image_type: Literal["chart", "image", "diagram", "screenshot"]


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def chat(self, messages: List, model: str = "gpt-4o",
             temperature: float = 0.7) -> str:
        try:
            response = self.client.responses.create(
                model=model,
                input=messages,
                temperature=temperature,
            )
            return response.output_text
        except Exception as e:
            print(f"Error during chat: {str(e)}")
            raise e

    def structured_chat(self, system: str, user: str,
                        structured_response: ResponseFormatT,
                        model: str = "gpt-4o") -> BaseModel:
        try:
            response = self.client.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format=structured_response,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            print(f"Error during structured chat: {str(e)}")
            raise e

    def image_description(
            self,
            image_bytes: bytes,
            model: str = "gpt-4o",
            max_tokens: int = 1000
    ) -> ResponseModel:
        try:
            mime_type = mimetypes.guess_type("file.png")[0] or "image/jpeg"
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = self.client.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": image_description_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                response_format=ResponseModel,
            )

            return response.choices[0].message.parsed
        except Exception as e:
            print(f"Error during image description: {str(e)}")
            raise e

