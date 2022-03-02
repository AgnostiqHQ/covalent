from datetime import datetime
from typing import Any, List, Optional, Sequence

from pydantic import BaseModel


class RunTaskResponse(BaseModel):
    response: str


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


class ResultList(BaseModel):
    list_of_results: List[Result]


class CancelResponse(BaseModel):
    cancelled_dispatch_id: str


class TaskStatus(BaseModel):
    status: str
