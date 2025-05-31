from pydantic import BaseModel


class PromptDataBase(BaseModel):
    pass

class TaskData(BaseModel):
    task_type: str
    api_key: str