from pydantic import BaseModel
from datetime import datetime
from lora.schemas import ILoraExtended
from enums import OutputFormat, OutputType

class PromptData(BaseModel):
    positivePrompt: str
    negativePrompt: str

class TaskData(BaseModel):
    task_type: str
    api_key: str

class BaseSDModel(BaseModel):
    air: str
    link: str
    shortname: str

class UserImgGenSettings(BaseModel):
    includeCost: bool
    outputQuality: int
    steps: int
    CFGScale: float
    clipSkip: int
    numberResults: int
    height: int
    width: int
    model: BaseSDModel
    scheduler: str
    lora: list[ILoraExtended]


class UserSettings(UserImgGenSettings):
    last_request_datetime: datetime | None = None
    outputFormat: OutputFormat
    outputType: OutputType

