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

"""
Defines the core functionality of the dispatcher
"""


from covalent._results_manager import Result

from . import runner


async def _get_task_inputs(node_id: int, node_name: str, result_object: Result) -> dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        node_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_object: Result object to be used to update and store execution related
                       info including the results.

    Returns:
        inputs: Input dictionary to be passed to the task containing args, kwargs,
                and any parent node execution results if present.
    """

    abstract_inputs = {"args": [], "kwargs": {}}

    for parent in result_object.lattice.transport_graph.get_dependencies(node_id):
        edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)
        # value = result_object.lattice.transport_graph.get_node_value(parent, "output")

        for e_key, d in edge_data.items():
            if not d.get("wait_for"):
                if d["param_type"] == "arg":
                    abstract_inputs["args"].append((parent, d["arg_index"]))
                elif d["param_type"] == "kwarg":
                    key = d["edge_name"]
                    abstract_inputs["kwargs"][key] = parent

    sorted_args = sorted(abstract_inputs["args"], key=lambda x: x[1])
    abstract_inputs["args"] = [x[0] for x in sorted_args]

    input_values = await runner._get_task_input_values(result_object.dispatch_id, abstract_inputs)

    abstract_args = abstract_inputs["args"]
    abstract_kwargs = abstract_inputs["kwargs"]
    args = [input_values[node_id] for node_id in abstract_args]
    kwargs = {k: input_values[v] for k, v in abstract_kwargs.items()}
    task_input = {"args": args, "kwargs": kwargs}

    return task_input
