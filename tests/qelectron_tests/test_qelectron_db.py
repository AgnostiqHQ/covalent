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

import pennylane as qml

import covalent as ct


def test_db_exposed_in_result():
    """
    Check that the QElectron database is correctly exposed in the result object.
    """

    # Define a QElectron circuit.
    qexecutor = ct.executor.QiskitExecutor(device="local_sampler")  # pylint: disable=no-member

    @ct.qelectron(executors=qexecutor)
    @qml.qnode(qml.device("default.qubit", wires=1))
    def circuit(param):
        qml.RZ(param, wires=0)
        return qml.expval(qml.PauliZ(0))

    # Define workflow electrons and lattice.
    @ct.electron
    def task_0_qe(param):
        # Run the QElectron circuit and return the result.
        return circuit(param)

    @ct.electron
    def task_1_qe(param):
        # Run the QElectron (10x) circuit and return the result.
        params = [param * (1 + i / 10) for i in range(10)]
        return [circuit(_param) for _param in params]

    @ct.electron
    def task_2():
        # Returns a non-QElectron result.
        return 46 + 2

    @ct.lattice
    def workflow(param):
        return task_0_qe(param), task_1_qe(param), task_2()

    # Define expected number of entries in the QElectron database.
    num_entries = {
        "task_0_qe": 1,
        "task_1_qe": 10,
        "task_2": 0,
    }

    # Dispatch workflow.
    dispatch_id = ct.dispatch(workflow)(0.5)
    result_obj = ct.get_result(dispatch_id, wait=True)

    # Check results.
    for result_dict in result_obj.get_all_node_results():

        if (node_name := result_dict["node_name"]) in num_entries:

            if node_name == "task_2":
                # Non-QElectron task should have no qelectron data.
                assert result_dict["qelectron"] is None
            else:
                # QElectron tasks should have qelectron data.
                assert result_dict["qelectron"] is not None

                # Number of entries should match number of executions.
                assert len(result_dict["qelectron"]) == num_entries[node_name]
