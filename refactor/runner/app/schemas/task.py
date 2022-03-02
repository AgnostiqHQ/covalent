from typing import List

from pydantic import BaseModel


class RunTaskResponse(BaseModel):
    response: str


class NodeID(BaseModel):
    id: int


class NodeIDList(BaseModel):
    list_node_ids: List[NodeID]


class CancelResponse(BaseModel):
    cancelled_dispatch_id: str


class TaskStatus(BaseModel):
    status: str
