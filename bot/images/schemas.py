from enums import OutputFormat, OutputType
from pydantic import BaseModel, Field
from schemas import PromptDataBase

class ImgToTextData(PromptDataBase):
    positive_prompt: str
    negative_prompt: str | None = None
    output_format: OutputFormat | None = OutputFormat.jpg
    output_type: OutputType | None = OutputType.url
    output_quality: int | None = Field(default=95, ge=20, le=100)
    check_nsfw: bool | None = False
    include_cost: bool | None = False

class ImgToTextResponse(BaseModel):
    caption: str
    image_url: str

class Model(BaseModel):