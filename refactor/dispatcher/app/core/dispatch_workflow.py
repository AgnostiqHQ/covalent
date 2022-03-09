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

from copy import deepcopy
from typing import Dict, List

from covalent._dispatcher_plugins import BaseDispatcher
from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph

from .utils import (
    get_sublattice,
    get_task_inputs,
    get_task_order,
    is_sublattice,
    preprocess_transport_graph,
)


def dispatch_workflow(result_obj: Result) -> Result:
    """Responsible for starting off the workflow dispatch."""

    if result_obj.status == Result.NEW_OBJ:
        result_obj = init_result_pre_dispatch(result_obj=result_obj)
        result_obj._status = Result.RUNNING
        result_obj = _dispatch_tasks(result_obj=result_obj)

    elif result_obj.status == Result.COMPLETED:
        # TODO - Redispatch workflow for reproducibility

        pass

    elif result_obj.status == Result.CANCELLED:
        # TODO - Redispatch cancelled workflow

        # Change status to running if we want to redeploy this workflow
        result_obj._status = Result.RUNNING

        # TODO - Redispatch tasks

    elif result_obj.status == Result.FAILED:
        # TODO - Redispatch failed workflow

        pass

    return result_obj


def _dispatch_tasks(result_obj: Result) -> Result:
    """Responsible for preprocessing the tasks, and sending the tasks for execution to the
    Runner API in batches. One of the underlying principles is that the Runner API doesn't
    interact with the Data API."""

    task_order: List[List] = get_task_order(result_obj=result_obj)

    while not (
        task_order or result_obj.status == Result.CANCELLED or result_obj.status == Result.FAILED
    ):
        tasks = task_order.pop(0)
        input_args = []
        executors = []

        for task_id in tasks:
            task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")
            inputs = get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)
            executor = result_obj.lattice.transport_graph.get_node_value(task_id, "metadata")[
                "executor"
            ]

            if is_sublattice(task_name=task_name):

                # TODO - Is deepcopy necessary here?
                sublattice = deepcopy(get_sublattice(task_id=task_id, result_obj=result_obj))

                sublattice.build_graph(inputs)

                sublattice_result_obj = Result(
                    lattice=sublattice,
                    results_dir=result_obj.lattice.metadata["results_dir"],
                    dispatch_id=f"{result_obj.dispatch_id}:{task_id}",
                )

                _dispatch_tasks(result_obj=sublattice_result_obj)

            else:
                preprocess_transport_graph(
                    task_id=task_id, task_name=task_name, result_obj=result_obj
                )
                input_args.append(inputs)
                executors.append(executor)

        # Dispatching batch of tasks to the Runner API.
        _run_task(
            result_obj=result_obj,
            task_id_batch=tasks,
            input_arg_batch=input_args,
            executors=executors,
        )

    return result_obj


def _run_task(
    result_obj: Result,
    task_id_batch: List[int],
    input_arg_batch: List[Dict],
    executors: List[BaseDispatcher],
):
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    pass


def init_result_pre_dispatch(result_obj: Result):
    """Initialize the result object transport graph before it is dispatched for execution."""

    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_obj.lattice.transport_graph)
    result_obj._lattice.transport_graph = transport_graph
    result_obj._initialize_nodes()
    return result_obj
