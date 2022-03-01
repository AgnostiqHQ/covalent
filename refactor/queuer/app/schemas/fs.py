from typing import Sequence, Any, Optional
from pydantic import BaseModel, HttpUrl

from datetime import datetime


class UploadResponse(BaseModel):
    filename: str
    path: str