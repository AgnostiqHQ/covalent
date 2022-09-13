# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Lattice request and response model"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class LatticeDetailResponse(BaseModel):
    """Lattices details model"""

    dispatch_id: str = None
    status: str = None
    total_electrons: int = None
    total_electrons_completed: int = None
    started_at: datetime = None
    ended_at: datetime = None
    directory: str = None
    description: str = None
    runtime: int = None
    updated_at: datetime = None


class LatticeFileResponse(BaseModel):
    """Lattices File Response Model"""

    data: str = None


class LatticeExecutorResponse(BaseModel):
    """Lattices File Response Model"""

    executor_name: str = None
    executor_details: dict = None


class LatticeWorkflowExecutorResponse(BaseModel):
    """Lattices File Response Model"""

    workflow_executor_name: str = None
    workflow_executor_details: dict = None


class GraphResponse(BaseModel):
    """Graph Response Model"""

    dispatch_id: str = None
    graph: dict = None


class ElectronResponse(BaseModel):
    """Electron Response Model"""

    id: int = None
    node_id: int = None
    parent_lattice_id: int = None
    type: str = None
    storage_path: str = None
    name: str = None
    status: str = None
    started_at: datetime = None
    ended_at: datetime = None
    runtime: int = None
    description: str = None


class ElectronFileResponse(BaseModel):
    """Electron Response Model"""

    data: str = None


class ElectronExecutorResponse(BaseModel):
    """Lattices File Response Model"""

    executor_name: str = None
    executor_details: dict = None


class ElectronErrorResponse(BaseModel):
    """Eelctron Error Response Model"""

    data: str = None


class ElectronFunctionResponse(BaseModel):
    """Electron Function Response Model"""

    data: str = None


class FileOutput(str, Enum):
    RESULT = "result"
    FUNCTION_STRING = "function_string"
    INPUTS = "inputs"
    ERROR = "error"
    EXECUTOR = "executor"
    WORKFLOW_EXECUTOR = "workflow_executor"
    FUNCTION = "function"
    TRANSPORT_GRAPH = "transport_graph"
