from pydantic import BaseModel, HttpUrl

class DispatchResponse(BaseModel):
    dispatch_id: str
