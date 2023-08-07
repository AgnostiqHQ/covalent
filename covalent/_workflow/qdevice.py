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

from typing import Sequence

from pennylane import QubitDevice
from pennylane import numpy as np
from pennylane.devices.default_qubit import DefaultQubit
from pennylane.gradients import param_shift

from ..quantum.qclient.core import middleware


class QEDevice(QubitDevice):

    """
    Custom Pennylane device that batch executes circuits by submitting them to the middleware
    """

    name = "QEDevice"
    short_name = "qe_device"
    pennylane_requires = ">=0.29.1"
    version = "0.0.1"
    author = "aq"

    operations = DefaultQubit.operations
    observables = DefaultQubit.observables

    def __init__(
        self,
        wires=1,
        shots=None,
        *,
        r_dtype=np.float64,  # pylint: disable=no-member
        c_dtype=np.complex128,  # pylint: disable=no-member
        analytic=None,
        executors=None,
        qelectron_info=None,
    ):
        super().__init__(wires, shots, r_dtype=r_dtype, c_dtype=c_dtype, analytic=analytic)

        self._async_run = False
        self._batch_id = None
        self.executors = executors
        self.qelectron_info = qelectron_info

        # This will be set when the QNodeQE
        # is called with args and kwargs
        self.qnode_specs = None

    def batch_execute(self, circuits):

        # Async submit all circuits to middleware.
        batch_id = middleware.run_circuits_async(
            circuits, self.executors, self.qelectron_info, self.qnode_specs
        )

        # Relevant when `run_later` is used to run the circuit.
        # We will retrieve the result later using the future object and the batch_id.
        if self._async_run:
            self._batch_id = batch_id

            # Return a (recognizable) dummy result
            res = [self._asarray([-123.456] * c.output_dim) for c in circuits]
            if isinstance(self.qelectron_info.device_shots, Sequence):
                # Replicate the list for shot vector case.
                return [[res]] * len(self.qelectron_info.device_shots)
            return res

        # Otherwise, get the results from the middleware
        results = middleware.get_results(batch_id)

        return results

    def gradients(self, circuits, method="jacobian", **kwargs):
        # Obtain gradient tapes and processing functions.
        grad_tapes_tuple, processing_fns = zip(
            *(param_shift(circuit, **kwargs) for circuit in circuits)
        )

        # Flatten the list of gradient tapes.
        nonempty_grad_tapes_list = []
        for grad_tapes in grad_tapes_tuple:
            nonempty_grad_tapes_list.extend(grad_tapes)

        # Skip gradient computation for vectorized calls.
        # Also require nonempty list of gradient tapes.
        scalar_input = all(not circuit.batch_size for circuit in circuits)
        if not (scalar_input and nonempty_grad_tapes_list):
            return []

        # Submit gradient circuits to middleware.
        nonempty_grad_res = self.batch_execute(nonempty_grad_tapes_list)

        # Unpack the nonempty gradient result into the expected shape.
        grad_res = self._unpack_gradient_result(nonempty_grad_res, grad_tapes_tuple)

        # Compute parameter-shift jacobians.
        jacs = [fn(r) for r, fn in zip(grad_res, processing_fns)]

        return jacs

    def _unpack_gradient_result(self, nonzero_grads, grad_tapes_tuple):
        """
        Unpack the gradient tapes' execution results into a list containing arrays
        and lists of arrays. Insert zero-arrays for empty gradient tapes.
        """
        grad_res = []
        zero_arr = self._asarray(0.)
        nonempty_idx = 0
        for grad_tapes in grad_tapes_tuple:
            if not grad_tapes:
                grad_res.append(zero_arr)
            else:
                sub_res = []
                for _ in grad_tapes:
                    sub_res.append(nonzero_grads[nonempty_idx])
                    nonempty_idx += 1

                sub_res = sub_res[0] if len(sub_res) == 1 else sub_res
                grad_res.append(sub_res)

        return grad_res

    def apply(self, *args, **kwargs):
        # Dummy implementation of abstractmethod on `QubitDevice`
        pass

    @classmethod
    def capabilities(cls):
        capabilities = super().capabilities().copy()
        capabilities.update(supports_broadcasting=True)
        return capabilities
