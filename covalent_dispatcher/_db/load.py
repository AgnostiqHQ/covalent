# Copyright 2023 Agnostiq Inc.
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

"""Functions to load results from the database."""


from typing import Dict, Union

from covalent import lattice
from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.util_classes import Status
from covalent._workflow.transport import TransportableObject
from covalent._workflow.transport import _TransportGraph as SDKGraph

from .._dal.electron import ASSET_KEYS as ELECTRON_ASSETS
from .._dal.electron import METADATA_KEYS as ELECTRON_META
from .._dal.result import get_result_object
from .._dal.tg import _TransportGraph as SRVGraph
from .._object_store.local import local_store
from .datastore import workflow_db
from .models import Electron, Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info

NODE_ATTRIBUTES = ELECTRON_META.union(ELECTRON_ASSETS)
SDK_NODE_META_KEYS = {
    "executor",
    "executor_data",
    "deps",
    "call_before",
    "call_after",
}


def load_file(storage_path, filename):
    return local_store.load_file(storage_path, filename)


def _to_client_graph(srv_graph: SRVGraph) -> SDKGraph:
    """Render a SDK _TransportGraph from a server-side graph"""

    sdk_graph = SDKGraph()

    sdk_graph._graph = srv_graph.get_internal_graph_copy()
    for node_id in srv_graph._graph.nodes:
        attrs = list(sdk_graph._graph.nodes[node_id].keys())
        for k in attrs:
            del sdk_graph._graph.nodes[node_id][k]
        attributes = {}
        for k in NODE_ATTRIBUTES:
            if k not in SDK_NODE_META_KEYS:
                attributes[k] = srv_graph.get_node_value(node_id, k)
        if srv_graph.get_node_value(node_id, "type") == "parameter":
            attributes["value"] = srv_graph.get_node_value(node_id, "value")
            attributes["output"] = srv_graph.get_node_value(node_id, "output")

        node_meta = {k: srv_graph.get_node_value(node_id, k) for k in SDK_NODE_META_KEYS}
        attributes["metadata"] = node_meta

        for k, v in attributes.items():
            sdk_graph.set_node_value(node_id, k, v)

        sdk_graph.lattice_metadata = {}

    return sdk_graph


def _result_from(lattice_record: Lattice) -> Result:
    """Re-hydrate result object from the lattice record.

    Args:
        lattice_record: Lattice record to re-hydrate from.

    Returns:
        Result object.

    """

    srv_res = get_result_object(lattice_record.dispatch_id, bare=False)

    function = srv_res.lattice.get_value("workflow_function")

    function_string = srv_res.lattice.get_value("workflow_function_string")
    function_docstring = srv_res.lattice.get_value("doc")

    executor_data = srv_res.lattice.get_value("executor_data")

    workflow_executor_data = srv_res.lattice.get_value("workflow_executor_data")

    inputs = srv_res.lattice.get_value("inputs")
    named_args = srv_res.lattice.get_value("named_args")
    named_kwargs = srv_res.lattice.get_value("named_kwargs")
    error = srv_res.get_value("error")

    transport_graph = _to_client_graph(srv_res.lattice.transport_graph)

    output = srv_res.get_value("result")
    deps = srv_res.lattice.get_value("deps")
    call_before = srv_res.lattice.get_value("call_before")
    call_after = srv_res.lattice.get_value("call_after")
    cova_imports = srv_res.lattice.get_value("cova_imports")
    lattice_imports = srv_res.lattice.get_value("lattice_imports")

    name = lattice_record.name
    executor = lattice_record.executor
    workflow_executor = lattice_record.workflow_executor
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
        },
        "inputs": inputs,
        "named_args": named_args,
        "named_kwargs": named_kwargs,
        "transport_graph": transport_graph,
        "cova_imports": cova_imports,
        "lattice_imports": lattice_imports,
        "post_processing": False,
        "electron_outputs": {},
        "_bound_electrons": {},
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
    result._error = error or ""
    result._inputs = inputs
    result._start_time = lattice_record.started_at
    result._end_time = lattice_record.completed_at
    result._result = output if output is not None else TransportableObject(None)
    result._num_nodes = num_nodes
    return result


def get_result_object_from_storage(dispatch_id: str) -> Result:
    """Get the result object from the database.

    Args:
        dispatch_id: The dispatch id of the result object to load.

    Returns:
        The result object.

    """
    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        if not lattice_record:
            app_log.debug(f"No result object found for dispatch {dispatch_id}")
            raise RuntimeError(f"No result object found for dispatch {dispatch_id}")

        return _result_from(lattice_record)


def electron_record(dispatch_id: str, node_id: str) -> Dict:
    """Get electron record for a given dispatch if and node id.

    Args:
        dispatch_id: Dispatch id for lattice.
        node_id: Node id of the electron.

    Returns:
        Electron record.

    """
    with workflow_db.session() as session:
        return (
            session.query(Lattice, Electron)
            .filter(Lattice.id == Electron.parent_lattice_id)
            .filter(Lattice.dispatch_id == dispatch_id)
            .filter(Electron.transport_graph_node_id == node_id)
            .first()
            .Electron.__dict__
        )


def sublattice_dispatch_id(electron_id: int) -> Union[str, None]:
    """Get the dispatch id of the sublattice for a given electron id.

    Args:
        electron_id: Electron ID.

    Returns:
        Dispatch id of sublattice. None, if the electron is not a sublattice.

    """
    with workflow_db.session() as session:
        if record := (session.query(Lattice).filter(Lattice.electron_id == electron_id).first()):
            return record.dispatch_id
