# Copyright 2023 Agnostiq Inc.
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
Quantum Server Implementation: Handles the async execution of quantum circuits.
"""

import datetime
import uuid
from asyncio import Task
from typing import Callable, List, Tuple

from pennylane.tape import QuantumScript

from ..._shared_files.qinfo import QElectronInfo, QNodeSpecs
from ..._shared_files.utils import (
    cloudpickle_deserialize,
    cloudpickle_serialize,
    select_first_executor,
)
from ...executor.utils import get_context
from ..qcluster.base import AsyncBaseQCluster, BaseQExecutor
from .database import Database
from .utils import CircuitInfo, get_cached_executor, get_circuit_id


class FuturesTable:
    """
    Container for async task futures corresponding to a sub-batch of executing
    qscripts, as identified by a batch UUID.
    """

    def __init__(self):
        self._ef_pairs = {}

    def add_executor_future_pairs(
        self,
        executor_future_pairs: List[Tuple[BaseQExecutor, Task]],
        submission_order: List[int],
    ) -> str:
        """
        Add a list of futures to the table and return a corresponding UUID.
        """
        batch_id = str(uuid.uuid4())
        self._ef_pairs[batch_id] = (executor_future_pairs, submission_order)
        return batch_id

    def pop_executor_future_pairs(
        self,
        batch_id: str,
    ) -> Tuple[List[Tuple[BaseQExecutor, Task]], List[int]]:
        """
        Retrieve a list of futures from the table using a UUID.
        """
        return self._ef_pairs.pop(batch_id)


class QServer:
    """
    Initialize a QServer instance with a given selector function.
    """

    # def __init__(self, selector: BaseQSelector = None) -> None:
    def __init__(self, selector: Callable = None) -> None:
        self.futures_table = FuturesTable()

        # self._selector = selector or SimpleSelector(selector_function=select_first_executor)
        self._selector = selector or select_first_executor
        self._database = Database()

    @property
    def selector(self):
        """
        Executor selector function for the Quantum server.
        """
        return self._selector

    @selector.setter
    def selector(self, ser_selector):
        self._selector = self.deserialize(ser_selector)

    @property
    def database(self):
        """Return the database for reading."""
        return self.serialize(self._database)

    def select_executors(
        self,
        qscripts: List[QuantumScript],
        executors: List[BaseQExecutor],
        qnode_specs: QNodeSpecs,
    ):
        """
        Links qscripts with an executor
        based on the self.selector function
        """

        linked_executors = []
        for qscript in qscripts:
            selected_executor = self.selector(qscript, executors)

            # Use cached executor.
            selected_executor = get_cached_executor(**selected_executor.dict())

            if isinstance(selected_executor, AsyncBaseQCluster):
                # Apply QCluster's selector as well.
                qcluster = selected_executor
                selected_executor = qcluster.get_selector()(qscript, qcluster.executors)

                # Use cached executor.
                selected_executor = get_cached_executor(**selected_executor.dict())

            # This is the only place where the qnode_specs are set.
            selected_executor.qnode_specs = qnode_specs.copy()

            # An example `linked_executors` will look like:
            # [exec_4, exec_4, exec_2, exec_3]
            # Their indices corresponding to the indices of `qscripts`.
            linked_executors.append(selected_executor)

        return linked_executors

    def submit_to_executors(
        self,
        qscripts: List[QuantumScript],
        linked_executors: List[BaseQExecutor],
        qelectron_info: QElectronInfo,
    ):
        """
        Generates futures for scheduled execution
        of qscripts on respective executors
        """

        # Since we will be modifying the qscripts list (or sometimes tuple).
        qscripts = list(qscripts).copy()

        submission_order = []
        executor_qscript_sub_batch_pairs = []
        for i, qscript in enumerate(qscripts):
            if qscript is None:
                continue

            # Generate a sub batch of qscripts to be executed on the same executor
            qscript_sub_batch = [linked_executors[i], {i: qscript}]

            # The qscript submission order is stored in this list to ensure that
            # the final result is recombined correctly, even if task-circuit
            # correspondence is not one-to-one. See, for example, PR #13.
            submission_order.append(i)

            for j in range(i + 1, len(qscripts)):
                if linked_executors[i] == linked_executors[j]:
                    qscript_sub_batch[1][j] = qscripts[j]
                    qscripts[j] = None
                    submission_order.append(j)

            # An example `qscript_sub_batch` will look like:
            # [exec_4, {0: qscript_1, 3: qscript_4}]

            executor_qscript_sub_batch_pairs.append(qscript_sub_batch)

        # An example `executor_qscript_sub_batch_pairs` will look like:
        # [
        #    [exec_4, {0: qscript_1, 3: qscript_4}],
        #    [exec_2, {2: qscript_3}],
        #    [exec_3, {4: qscript_5}],
        # ]

        # Generating futures from each executor:
        executor_future_pairs = []
        for executor, qscript_sub_batch in executor_qscript_sub_batch_pairs:
            executor.qelectron_info = qelectron_info.copy()
            qscript_futures = executor.batch_submit(qscript_sub_batch.values())

            futures_dict = dict(zip(qscript_sub_batch.keys(), qscript_futures))
            # An example `futures_dict` will look like:
            # {0: future_1, 3: future_4}

            executor_future_pairs.append([executor, futures_dict])

        # An example `executor_future_pairs` will look like:
        # [[exec_4, {0: future_1, 3: future_4}], [exec_2, {2: future_3}], [exec_3, {4: future_5}]]

        return executor_future_pairs, submission_order

    def submit(
        self,
        qscripts: List[QuantumScript],
        executors: List[BaseQExecutor],
        qelectron_info: QElectronInfo,
        qnode_specs: QNodeSpecs,
    ):
        # pylint: disable=too-many-locals
        """
        Submit a list of QuantumScripts to the server for execution.

        Args:
            qscripts: A list of QuantumScripts to run.
            executors: The executors to choose from to use for running the QuantumScripts.
            qelectron_info: Information about the qelectron as provided by the user.
            qnode_specs: Specifications of the qnode.

        Returns:
            str: A UUID corresponding to the batch of submitted QuantumScripts.
        """

        # Get current electron's context
        context = get_context()

        # Get qelectron info, qnode specs, quantum scripts, and executors
        qelectron_info = self.deserialize(qelectron_info)
        qnode_specs = self.deserialize(qnode_specs)
        qscripts = self.deserialize(qscripts)
        executors = self.deserialize(executors)

        # Generate a list of executors for each qscript.
        linked_executors = self.select_executors(qscripts, executors, qnode_specs)

        # Assign qscript sub-batches to unique executors.
        executor_future_pairs, submission_order = self.submit_to_executors(
            qscripts, linked_executors, qelectron_info
        )

        # Get batch ID for N qscripts being async-executed on M <= N executors.
        batch_id = self.futures_table.add_executor_future_pairs(
            executor_future_pairs, submission_order
        )

        # Storing the qscripts, executors, and metadata in the database
        batch_time = str(datetime.datetime.now())
        key_value_pairs = [[], []]

        for i, qscript in enumerate(qscripts):
            circuit_id = get_circuit_id(batch_id, i)
            key_value_pairs[0].append(circuit_id)
            circuit_info = CircuitInfo(
                electron_node_id=context.task_id,
                dispatch_id=context.dispatch_id,
                circuit_name=qelectron_info.name,
                circuit_description=qelectron_info.description,
                circuit_diagram=qscript.draw(),
                qnode_specs=qnode_specs,
                qexecutor=linked_executors[i],
                save_time=batch_time,
                circuit_id=circuit_id,
                qscript=qscript.graph.serialize() if linked_executors[i].persist_data else None,
            ).dict()

            key_value_pairs[1].append(circuit_info)

        # An example `key_value_pairs` will look like:
        # [
        #     [
        #         "circuit_0-uuid",
        #         "circuit_1-uuid",
        #
        #         ...
        #     ],
        #     [
        #         {"electron_node_id": "node_1",
        #          "dispatch_id": "uuid",
        #          "circuit_name": "qscript_name",
        #          "circuit_description": "qscript_description",
        #          "qnode_specs": {"qnode_specs": "specs"},
        #          "qexecutor": "executor_1",
        #          "save_time": "2021-01-01 00:00:00",
        #          "circuit_id": "circuit_0-uuid",
        #          "qscript": "qscript_1"},

        #         {"electron_node_id": "node_1",
        #          "dispatch_id": "uuid",
        #          "circuit_name": "qscript_name",
        #          "circuit_description": "qscript_description",
        #          "qnode_specs": {"qnode_specs": "specs"},
        #          "qexecutor": "executor_2",
        #          "save_time": "2021-01-01 00:00:00",
        #          "circuit_id": "circuit_1-uuid",
        #          "qscript": "qscript_2"},
        #
        #         ...
        #     ],
        # ]

        self._database.set(
            *key_value_pairs, dispatch_id=context.dispatch_id, node_id=context.task_id
        )

        return batch_id

    def get_results(self, batch_id):
        # pylint: disable=too-many-locals
        """
        Retrieve the results of previously submitted QuantumScripts from the server.

        Args:
            batch_id: The UUID corresponding to the batch of submitted QuantumScripts.

        Returns:
            List: An ordered list of results for the submitted QuantumScripts.
        """

        # Get current electron's context
        context = get_context()

        results_dict = {}
        key_value_pairs = [[], []]
        executor_future_pairs, submission_order = self.futures_table.pop_executor_future_pairs(
            batch_id
        )

        # ids of (e)xecutor_(f)uture_(p)airs, hence `idx_efp`
        qscript_submission_index = 0
        for idx_efp, (executor, futures_sub_batch) in enumerate(executor_future_pairs):
            result_objs = executor.batch_get_results(futures_sub_batch.values())

            # Adding results according to the order of the qscripts
            # ids of (f)utures_(s)ub_(b)atch, hence `idx_fsb`
            for idx_fsb, circuit_number in enumerate(futures_sub_batch.keys()):
                result_obj = result_objs[idx_fsb]

                # Expand `result_obj` in case contains multiple circuits.
                # Loop through sub-results to store separately in db.
                for result_number, sub_result_obj in enumerate(result_obj.expand()):
                    qscript_number = submission_order[qscript_submission_index]

                    # Use tuple of integers for key to enable later multi-factor sort.
                    key = (qscript_number, circuit_number, result_number)
                    results_dict[key] = sub_result_obj.results[0]
                    qscript_submission_index += 1

                    # To store the results in the database
                    circuit_id = get_circuit_id(batch_id, circuit_number + result_number)
                    key_value_pairs[0].append(circuit_id)
                    key_value_pairs[1].append(
                        {
                            "execution_time": sub_result_obj.execution_time,
                            "result": sub_result_obj.results if executor.persist_data else None,
                            "result_metadata": sub_result_obj.metadata
                            if executor.persist_data
                            else None,
                        }
                    )

            # An example `key_value_pairs` will look like:
            # [
            #     [
            #         "result_circuit_0-uuid",
            #         "result_circuit_1-uuid",
            #     ],
            #     [
            #         {"execution_time": "2021-01-01 00:00:00",
            #          "result": [result_11, ...],
            #          "result_metadata": [{}, ...]},
            #
            #         {"execution_time": "2021-01-01 00:00:00",
            #          "result": [result_21, ...],
            #          "result_metadata": [{}, ...]},
            #     ],
            # ]

            # Deleting the futures once their results have been retrieved
            del executor_future_pairs[idx_efp][1]

            # After deletion of one `future_sub_batch`, the `executor_future_pairs` will look like:
            # [[exec_4], [exec_2, {2: future_3}], [exec_3, {4: future_5}]]

        self._database.set(
            *key_value_pairs, dispatch_id=context.dispatch_id, node_id=context.task_id
        )

        # An example `results_dict` will look like:
        # {0: result_1, 3: result_4, 2: result_3, 4: result_5}

        # Perform multi-factor sort on `results_dict`.
        batch_results = list(dict(sorted(results_dict.items())).values())

        # An example `batch_results` will look like:
        # [result_1, result_2, result_3, result_4, result_5]

        return self.serialize(batch_results)

    def serialize(self, obj):
        """
        Serialize an object.
        """
        return cloudpickle_serialize(obj)

    def deserialize(self, obj):
        """
        Deserialize an object.
        """
        return cloudpickle_deserialize(obj)
