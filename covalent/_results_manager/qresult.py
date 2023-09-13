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

from typing import Any

import pennylane as qml
from pennylane.tape import QuantumTape

from .._shared_files.qresult_utils import re_execute
from ..quantum.qclient.core import middleware


class QNodeFutureResult:
    """
    A class that stores the `batch_id` of a batch of circuits submitted to the
    middleware. The `result` method can then be called to retrieve the results.

    Attributes:
        device: The Pennylane device used by the original QNode.
        interface: The interface of the original QNode.
        diff_method: The differentiation method of the original QNode.
        qfunc_output: The return value (measurement definition) of the original QNode.
    """

    def __init__(
        self,
        batch_id: str,
        interface: str,
        original_qnode: qml.QNode,
        original_tape: QuantumTape,
    ):
        """
        Initialize a `QNodeFutureResult` instance.

        Args:
            batch_id: A UUID that identifies a batch of circuits submitted to
                the middleware.
        """
        self.batch_id = batch_id
        self.interface = interface  # NOT the original QNode's interface

        # Required for batch_transforms and correct output typing.
        self.device = original_qnode.device
        self.qnode = original_qnode
        self.tape = original_tape

        self.args = None
        self.kwargs = None
        self._result = None

    def __call__(self, *args, **kwargs):
        """
        Store the arguments and keyword arguments of the original QNode call.
        """
        self.args = args
        self.kwargs = kwargs
        return self

    def result(self) -> Any:
        """
        Retrieve the results for the given `batch_id` from middleware. This method
        is blocking until the results are available.

        Returns:
            The results of the circuit execution.
        """

        if self._result is None:
            # Get raw results from the middleware.
            results = middleware.get_results(self.batch_id)

            # Required correct gradient post-processing in some cases.
            if self.interface == "autograd":
                self._result = results
                res = results[0]

            if self.interface != "numpy":
                interface = self.interface  # re-execute with any non-numpy interface
                res = results[0]  # re-execute with this result

            elif self.qnode.interface is None:
                interface = None
                res = results[0]

            elif self.qnode.interface == "auto":
                interface = "auto"
                res = results

            else:
                # Skip re-execution.
                self._result = results
                return results

            args, kwargs = self.args, self.kwargs
            self._result = re_execute(res, self.qnode, self.tape)(interface, *args, **kwargs)

        return self._result
