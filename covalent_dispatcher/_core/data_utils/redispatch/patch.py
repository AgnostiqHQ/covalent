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

"""Utils for editing transport graphs"""


from covalent._results_manager import Result
from covalent._workflow.transport import TransportableObject, _TransportGraph


def _replace_node(tg: _TransportGraph, node_id: int, new_attrs):
    metadata = tg.get_node_value(node_id, "metadata")
    new_metadata = new_attrs["metadata"]
    metadata.update(new_metadata)
    print(f"Replaced node {node_id} metadata")

    serialized_callable = TransportableObject.from_dict(new_attrs["function"])
    tg.set_node_value(node_id, "function", serialized_callable)
    print(f"Replaced node {node_id} function")

    function_string = new_attrs["function_string"]
    tg.set_node_value(node_id, "function_string", function_string)
    print(f"Replaced node {node_id} function string")

    name = new_attrs["name"]
    tg.set_node_value(node_id, "name", name)
    print(f"Replaced node {node_id} name")
    _reset_descendents(tg, node_id)
    print(f"Invalidated descendents of node {node_id}")


def _reset_node(tg: _TransportGraph, node_id: int):
    tg.set_node_value(node_id, "start_time", None)
    tg.set_node_value(node_id, "end_time", None)
    tg.set_node_value(node_id, "status", Result.NEW_OBJ)
    tg.set_node_value(node_id, "output", None)
    tg.set_node_value(node_id, "error", None)
    tg.set_node_value(node_id, "sub_dispatch_id", None)
    tg.set_node_value(node_id, "sublattice_result", None)
    tg.set_node_value(node_id, "stdout", None)
    tg.set_node_value(node_id, "stderr", None)


def _reset_descendents(tg, node_id):
    try:
        if tg.get_node_value(node_id, "status") == Result.NEW_OBJ:
            print("Encountered recursion base case")
            return
    except:
        return
    _reset_node(tg, node_id)
    for successor in tg._graph.neighbors(node_id):
        print("Resetting recursively")
        _reset_descendents(tg, successor)


def apply_electron_updates(tg: _TransportGraph, electron_updates: dict):
    for n in tg._graph.nodes:
        name = tg.get_node_value(n, "name")
        if name in electron_updates:
            _replace_node(tg, n, electron_updates[name])
    return tg


def copy_nodes(tg_old, tg_new, nodes):
    for n in nodes:
        for k, v in tg_old._graph.nodes[n].items():
            tg_new.set_node_value(n, k, v)
