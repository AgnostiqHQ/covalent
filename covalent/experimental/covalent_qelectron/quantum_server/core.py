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

import datetime
import uuid
from typing import TYPE_CHECKING, Callable, List

from pennylane.tape import QuantumScript

from ....executor.utils import get_context
from ..executors import BaseQExecutor
from ..quantum_server.database import Database
from ..quantum_server.server_utils import (
    CircuitInfo,
    get_cached_executor,
    get_circuit_id,
    reconstruct_executors,
)
from ..shared_utils import dummy_deserialize, dummy_serialize, select_first_executor

if TYPE_CHECKING:
    from covalent_qelectron.core.qelectron import QElectronInfo
    from covalent_qelectron.core.qnode_qe import QNodeSpecs


class FuturesTable:
    def __init__(self):
        self._ef_pairs = {}

    def add_executor_future_pairs(self, executor_future_pairs):
        """
        Add a list of futures to the table and return a corresponding UUID.
        """
        batch_id = str(uuid.uuid4())
        self._ef_pairs[batch_id] = executor_future_pairs
        return batch_id

    def pop_executor_future_pairs(self, batch_id):
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
        return self._selector

    @selector.setter
    def selector(self, ser_selector):
        self._selector = self.deserialize(ser_selector)

    @property
    def database(self):
        """Return the database for reading."""
        return self.serialize(self._database)

    def select_executors(self, qscripts: List[QuantumScript], executors: List[BaseQExecutor]):
        """
        Links qscripts with an executor
        based on the self.selector function
        """

        linked_executors = []
        for qscript in qscripts:
            selected_executor = self.selector(qscript, executors)
            linked_executors.append(get_cached_executor(**selected_executor.dict()))

        # An example `linked_executors` will look like:
        # [exec_4, exec_4, exec_2, exec_3]
        # Their indices corresponding to the indices of `qscripts`.

        return linked_executors

    def submit_to_executors(
        self, qscripts: List[QuantumScript],
        linked_executors: List[BaseQExecutor]
    ):
        """
        Generates futures for scheduled execution
        of qscripts on respective executors
        """

        # Since we will be modifying the qscripts list
        qscripts = qscripts.copy()

        executor_qscript_sub_batch_pairs = []
        for i, qscript in enumerate(qscripts):
            if qscript is None:
                continue

            # Generate a sub batch of qscripts to be executed on the same executor
            qscript_sub_batch = [linked_executors[i], {i: qscript}]
            for j in range(i + 1, len(qscripts)):
                if linked_executors[i] == linked_executors[j]:
                    qscript_sub_batch[1][j] = qscripts[j]
                    qscripts[j] = None

            # An example `qscript_sub_batch` will look like:
            # [exec_4, {0: qscript_1, 3: qscript_4}]

            executor_qscript_sub_batch_pairs.append(qscript_sub_batch)

        # An example `executor_qscript_sub_batch_pairs` will look like:
        # [[exec_4, {0: qscript_1, 3: qscript_4}], [exec_2, {2: qscript_3}], [exec_3, {4: qscript_5}]]

        # Generating futures from each executor:
        executor_future_pairs = []
        for executor, qscript_sub_batch in executor_qscript_sub_batch_pairs:
            qscript_futures = executor.batch_submit(qscript_sub_batch.values())

            futures_dict = dict(zip(qscript_sub_batch.keys(), qscript_futures))
            # An example `futures_dict` will look like:
            # {0: future_1, 3: future_4}

            executor_future_pairs.append([executor, futures_dict])

        # An example `executor_future_pairs` will look like:
        # [[exec_4, {0: future_1, 3: future_4}], [exec_2, {2: future_3}], [exec_3, {4: future_5}]]

        return executor_future_pairs

    def submit(
        self,
        qscripts: List[QuantumScript],
        executors: List[BaseQExecutor],
        qelectron_info: "QElectronInfo",
        qnode_specs: "QNodeSpecs"
    ):
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

        # Get qelectron info
        qelectron_info = self.deserialize(qelectron_info)

        # Get qnode specs
        qnode_specs = self.deserialize(qnode_specs)

        qscripts = self.deserialize(qscripts)

        deconstructed_executors = self.deserialize(executors)
        executors = reconstruct_executors(deconstructed_executors)

        linked_executors = self.select_executors(qscripts, executors)
        executor_future_pairs = self.submit_to_executors(qscripts, linked_executors)

        batch_id = self.futures_table.add_executor_future_pairs(executor_future_pairs)

        # Storing the qscripts, executors, and metadata in the database
        batch_time = str(datetime.datetime.now())
        key_value_pairs = [[], []]

        for i, qscript in enumerate(qscripts):
            circuit_id = get_circuit_id(batch_id, i)
            key_value_pairs[0].append(circuit_id)
            circuit_info = CircuitInfo(
                electron_node_id=context.node_id,
                dispatch_id=context.dispatch_id,
                circuit_name=qelectron_info.name,
                circuit_description=qelectron_info.description,
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
        #         "circuit_2-uuid"
        #     ],
        #     [
        #         {"electron_node_id": "node_1", "dispatch_id": "uuid", "circuit_name": "qscript_name",
        #          "circuit_description": "qscript_description", "qnode_specs": {"qnode_specs": "specs"},
        #          "qexecutor": "executor_1", "save_time": "2021-01-01 00:00:00", "circuit_id": "circuit_0-uuid",
        #          "qscript": "qscript_1"},

        #         {"electron_node_id": "node_1", "dispatch_id": "uuid", "circuit_name": "qscript_name",
        #          "circuit_description": "qscript_description", "qnode_specs": {"qnode_specs": "specs"},
        #          "qexecutor": "executor_2", "save_time": "2021-01-01 00:00:00", "circuit_id": "circuit_1-uuid",
        #          "qscript": "qscript_2"},

        #         {"electron_node_id": "node_1", "dispatch_id": "uuid", "circuit_name": "qscript_name",
        #          "circuit_description": "qscript_description", "qnode_specs": {"qnode_specs": "specs"},
        #          "qexecutor": "executor_3", "save_time": "2021-01-01 00:00:00", "circuit_id": "circuit_2-uuid",
        #          "qscript": "qscript_3"}
        #     ],
        # ]

        self._database.set(
            *key_value_pairs,
            dispatch_id=context.dispatch_id,
            node_id=context.node_id
        )

        return batch_id

    def get_results(self, batch_id):
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
        executor_future_pairs = self.futures_table.pop_executor_future_pairs(batch_id)

        # ids of (e)xecutor_(f)uture_(p)airs, hence `idx_efp`
        for idx_efp, (executor, futures_sub_batch) in enumerate(executor_future_pairs):

            result_objs = executor.batch_get_result_and_time(
                futures_sub_batch.values()
            )

            # Adding results according to the order of the qscripts
            # ids of (f)utures_(s)ub_(b)atch, hence `idx_fsb`
            for idx_fsb, circuit_number in enumerate(futures_sub_batch.keys()):

                # loop over result, in case contains multiple circuits
                result_obj = result_objs[idx_fsb]
                for result_number, sub_result in enumerate(result_obj.results):
                    results_dict[(circuit_number, result_number)] = sub_result

                # To store the results in the database
                circuit_id = get_circuit_id(batch_id, circuit_number)
                key_value_pairs[0].append(circuit_id)

                key_value_pairs[1].append(
                    {
                        "execution_time": result_obj.execution_time,
                        "result": result_obj.results if executor.persist_data else None,
                        "result_metadata": result_obj.metadata if executor.persist_data else None,
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
            *key_value_pairs,
            dispatch_id=context.dispatch_id,
            node_id=context.node_id
        )

        # An example `results_dict` will look like:
        # {0: result_1, 3: result_4, 2: result_3, 4: result_5}

        batch_results = list(dict(sorted(results_dict.items())).values())

        # An example `batch_results` will look like:
        # [result_1, result_2, result_3, result_4, result_5]

        return self.serialize(batch_results)

    def serialize(self, obj):
        return dummy_serialize(obj)

    def deserialize(self, obj):
        return dummy_deserialize(obj)
