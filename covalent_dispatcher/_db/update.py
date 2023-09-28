# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.defaults import postprocess_prefix
from covalent._shared_files.util_classes import Status
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph

from . import upsert

app_log = logger.app_log


def persist(record: Union[Result, Lattice, _TransportGraph], electron_id: int = None) -> None:
    """Save Result object to a DataStoreSession. Changes are queued until
    committed by the caller.

    Args:
        record: The entity to persist in the DB
        electron_id: (hack) DB-generated id for the parent electron
            if the workflow is actually a subworkflow
    """
    if isinstance(record, Result):
        _initialize_results_dir(record)
        app_log.debug("Persisting record...")
        upsert.persist_result(record, electron_id)
        app_log.debug("persist complete")
    if isinstance(record, Lattice):
        persist(record.transport_graph)
    if isinstance(record, _TransportGraph):
        record.dirty_nodes.clear()


def _node(
    result,
    node_id: int,
    node_name: str = None,
    start_time: "datetime" = None,
    end_time: "datetime" = None,
    status: "Status" = None,
    output: Any = None,
    error: Exception = None,
    sub_dispatch_id: str = None,
    sublattice_result: "Result" = None,
    stdout: str = None,
    stderr: str = None,
    qelectron_data_exists: bool = False,
) -> None:
    """
    Update the node result in the transport graph.
    Called after any change in node's execution state.

    Args:
        node_id: The node id.
        node_name: The name of the node.
        start_time: The start time of the node execution.
        end_time: The end time of the node execution.
        status: The status of the node execution.
        output: The output of the node unless error occurred in which case None.
        error: The error of the node if occurred else None.
        sublattice_result: The result of the sublattice if any.
        stdout: The stdout of the node execution.
        stderr: The stderr of the node execution.
        qelectron_data_exists: Flag indicating presence of Qelectron(s) inside the task

    Returns:
        None

    """
    if node_name is None:
        node_name = result.lattice.transport_graph.get_node_value(node_id, "name")

    result._update_node(
        node_id=node_id,
        node_name=node_name,
        start_time=start_time,
        end_time=end_time,
        status=status,
        output=output,
        error=error,
        sub_dispatch_id=sub_dispatch_id,
        sublattice_result=sublattice_result,
        stdout=stdout,
        stderr=stderr,
        qelectron_data_exists=qelectron_data_exists,
    )

    upsert.electron_data(result)

    if node_name.startswith(postprocess_prefix):
        app_log.warning(f"Persisting postprocess result {output}, node_name: {node_name}")
        result._result = output
        result._status = status
        result._end_time = end_time
        upsert.lattice_data(result)


def _initialize_results_dir(result):
    """Create the results directory."""

    result_folder_path = os.path.join(
        os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir"),
        f"{result.dispatch_id}",
    )
    Path(result_folder_path).mkdir(parents=True, exist_ok=True)
