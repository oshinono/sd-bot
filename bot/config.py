from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    token: str
    waiting_sticker_id: str
    debounce_seconds: int
    rw_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()