import os
from typing import List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):
    API_V0_STR: str = "/api/v0"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DB_URI")

    class Config:
        case_sensitive = True


settings = Settings()
