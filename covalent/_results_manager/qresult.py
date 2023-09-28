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
