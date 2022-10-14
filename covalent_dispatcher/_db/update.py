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

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.util_classes import Status
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph

from . import upsert
from .write_result_to_db import upsert_electron_dependency_data

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
        app_log.debug("upsert start")
        upsert._lattice_data(record, electron_id=electron_id)
        upsert._electron_data(record)
        app_log.debug("upsert complete")
        upsert_electron_dependency_data(record.dispatch_id, record.lattice)
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
    sublattice_result: "Result" = None,
    stdout: str = None,
    stderr: str = None,
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
        output: The output of the node unless error occured in which case None.
        error: The error of the node if occured else None.
        sublattice_result: The result of the sublattice if any.
        stdout: The stdout of the node execution.
        stderr: The stderr of the node execution.

    Returns:
        None
    """

    result._update_node(
        node_id=node_id,
        node_name=node_name,
        start_time=start_time,
        end_time=end_time,
        status=status,
        output=output,
        error=error,
        sublattice_result=sublattice_result,
        stdout=stdout,
        stderr=stderr,
    )

    upsert._electron_data(result)


def _initialize_results_dir(result):
    """Create the results directory."""

    result_folder_path = os.path.join(result.results_dir, f"{result.dispatch_id}")
    Path(result_folder_path).mkdir(parents=True, exist_ok=True)
