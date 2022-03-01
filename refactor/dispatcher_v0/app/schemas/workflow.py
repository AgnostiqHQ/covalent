from datetime import datetime
from typing import Sequence, Any, Optional
from pydantic import BaseModel, HttpUrl

class DispatchResponse(BaseModel):
    dispatch_id: str


class BaseNode(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    status: str
    output: Any
    error: Optional[str]
    stdout: str
    stderr: str


class Link(BaseNode):
    edge_name: str
    param_type: str
    source: int
    target: int

class Node(BaseNode):
    id: int
    
class Graph(BaseModel):
    nodes: Sequence[Node]
    links: Sequence[Link]

class Result(BaseModel):
    dispatch_id: str
    results_dir: str
    status: str
    graph: Graph


class UpdateWorkflowRequest(BaseModel):
    event: str

class UpdateWorkFlowResponse(UpdateWorkflowRequest):
    result: Result