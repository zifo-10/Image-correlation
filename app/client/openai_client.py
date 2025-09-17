import base64
import json
import mimetypes
from typing import Optional, List, Literal, Union


from openai import OpenAI
from openai.lib import ResponseFormatT
from pydantic import BaseModel, ConfigDict, Field
from app.constant_manager import image_description_prompt

# Structured response model
class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
class TableDataModel(StrictBaseModel):
    type: Literal["table"] = Field(default="table")
    headers: List[str] = Field(description="The headers of the table")
    data: List[List[str|int]] = Field(description="The data of the table")
    title: str = Field(description="The title of the table")
    caption: Optional[str] = Field(default=None, description="The caption of the table")


class ChartDataDetailsModel(StrictBaseModel):
    type: Literal["chart"] = Field(default="chart")
    labels: List[str|int] = Field(
        description="Labels of the chart",
    )
    datasets: List[float] = Field(
        description="Datasets of the chart",
    )

class ChartDataModel(StrictBaseModel):
    chart_type: Literal["bar", "line", "pie", "radar", "doughnut"] = Field(
        description="The type of the chart"
    )
    data: ChartDataDetailsModel = Field(description="The data of the chart")
    title: str = Field(description="The title of the chart")


class ImageModel(StrictBaseModel):
    type: Literal["image"] = Field(default="image")
    # url: str = Field(description="The url of the image")
    title: str = Field(description="The title of the image")
    alt_text: Optional[str] = Field(
        description="The alt text of the image", default=None)
    

class GeneratedVisualItemModel(StrictBaseModel):
    type: Literal["chart", "image", "table"] = Field(
        description="The type of the item")
    content: Union[ChartDataModel, ImageModel, TableDataModel] = Field(
        description="The content of the item")
    description: str = Field(description="The description of the image")
    
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
            formatted_prompt = image_description_prompt.format(response_schema=json.dumps(GeneratedVisualItemModel.model_json_schema()))
            response = self.client.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": formatted_prompt},
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
                response_format=GeneratedVisualItemModel,
            )

            return response.choices[0].message.parsed
        except Exception as e:
            print(f"Error during image description: {str(e)}")
            raise e

