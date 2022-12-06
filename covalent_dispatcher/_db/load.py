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

from typing import Optional

from covalent import lattice
from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.util_classes import Status
from covalent._workflow.transport import TransportableObject

from .datastore import workflow_db
from .models import Lattice
from .write_result_to_db import load_file

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def _result_from(lattice_record: Lattice) -> Result:
    """Re-hydrate result object from the lattice record."""

    function = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.function_filename
    )
    function_string = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.function_string_filename
    )
    function_docstring = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.docstring_filename
    )
    executor_data = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.executor_data_filename
    )
    workflow_executor_data = load_file(
        storage_path=lattice_record.storage_path,
        filename=lattice_record.workflow_executor_data_filename,
    )
    inputs = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.inputs_filename
    )
    named_args = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.named_args_filename
    )
    named_kwargs = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.named_kwargs_filename
    )
    error = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.error_filename
    )
    transport_graph = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.transport_graph_filename
    )
    output = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.results_filename
    )
    deps = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.deps_filename
    )
    call_before = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.call_before_filename
    )
    call_after = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.call_after_filename
    )
    cova_imports = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.cova_imports_filename
    )
    lattice_imports = load_file(
        storage_path=lattice_record.storage_path, filename=lattice_record.lattice_imports_filename
    )

    name = lattice_record.name
    executor = lattice_record.executor
    workflow_executor = lattice_record.workflow_executor
    results_dir = lattice_record.results_dir
    num_nodes = lattice_record.electron_num

    attributes = {
        "workflow_function": function,
        "workflow_function_string": function_string,
        "__name__": name,
        "__doc__": function_docstring,
        "metadata": {
            "executor": executor,
            "executor_data": executor_data,
            "workflow_executor": workflow_executor,
            "workflow_executor_data": workflow_executor_data,
            "deps": deps,
            "call_before": call_before,
            "call_after": call_after,
            "results_dir": results_dir,
        },
        "args": inputs["args"],
        "kwargs": inputs["kwargs"],
        "named_args": named_args,
        "named_kwargs": named_kwargs,
        "transport_graph": transport_graph,
        "cova_imports": cova_imports,
        "lattice_imports": lattice_imports,
        "post_processing": False,
        "electron_outputs": {},
    }

    def dummy_function(x):
        return x

    lat = lattice(dummy_function)
    lat.__dict__ = attributes

    result = Result(
        lat,
        dispatch_id=lattice_record.dispatch_id,
    )
    result._root_dispatch_id = lattice_record.root_dispatch_id
    result._status = Status(lattice_record.status)
    result._error = error if error else None
    result._inputs = inputs
    result._start_time = lattice_record.started_at
    result._end_time = lattice_record.completed_at
    result._result = output if output is not None else TransportableObject(None)
    result._num_nodes = num_nodes
    return result


def get_result_object_from_storage(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
):
    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        status = lattice_record.status if lattice_record else None
        if not lattice_record:
            app_log.debug(f"No result object found for dispatch {dispatch_id}")
            raise RuntimeError(f"No result object found for dispatch {dispatch_id}")

        return _result_from(lattice_record)
