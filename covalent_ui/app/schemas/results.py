from datetime import datetime
from typing import Any, Optional, Sequence

from pydantic import BaseModel


class BaseNode(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    status: str
    output: Any
    error: Optional[str]
    stdout: str
    stderr: str


class Link(BaseModel):
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
    status: str
    graph: Graph
