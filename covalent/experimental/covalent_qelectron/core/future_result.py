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

import pennylane as qml

from ..middleware.core import middleware


def _run_later_device(results, original_device):

    qml_device_cls = type(original_device)

    class _RunLaterDevice(qml_device_cls):
        # pylint: disable=too-few-public-methods

        def batch_execute(self, _):
            """
            Override to return expected result.
            """
            return results

    wires = original_device.num_wires
    shots = original_device.shots
    return _RunLaterDevice(wires=wires, shots=shots)



class QNodeFutureResult:

    def __init__(self, batch_id):
        self.batch_id = batch_id

        self.device = None
        self.interface = None
        self.diff_method = None
        self.qfunc_output = None

        self._result = None

    def result(self):
        """
        Retrieve the results from middleware for the given batch_id.

        Run the results through a dummy QNode to get the expected result type.

        Returns:
            Any: The results of the circuit execution.
        """

        if self._result is None:

            results = middleware.get_results(self.batch_id)
            dev = _run_later_device(results, self.device)

            @qml.qnode(dev, interface=self.interface, diff_method=self.diff_method)
            def _dummy_circuit():
                return self.qfunc_output

            self._result = _dummy_circuit()

        return self._result
