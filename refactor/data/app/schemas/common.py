from typing import Sequence, Any, Optional
from pydantic import BaseModel, HttpUrl

class HTTPExceptionSchema(BaseModel):
    detail: str