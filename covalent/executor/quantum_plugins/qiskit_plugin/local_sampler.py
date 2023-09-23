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

""""
Pennylane-Qiskit device that uses the local Qiskit `Sampler` primitive
"""

from typing import Any, List, Tuple

from devices_base import QiskitSamplerDevice
from qiskit.primitives import Sampler as LocalSampler


class QiskitLocalSampler(QiskitSamplerDevice):
    """
    Pennylane device that runs circuits using the local `qiskit.primitives.Sampler`
    """

    short_name = "local_sampler"

    def __init__(self, wires: int, shots: int, **_):
        self.circuit = None
        self.transpile_args = {}

        super().__init__(
            wires=wires,
            shots=shots,
            backend_name="None",
            local_transpile=False,
            transpile_backend=None,
            service_init_kwargs={},
        )

        self._metadatas = []

    def batch_execute(self, circuits, timeout: int = None):
        # pylint: disable=missing-function-docstring

        n_original_circuits = len(circuits)
        circuits = self.broadcast_tapes(circuits)
        n_circuits = len(circuits)

        # Create circuit objects and apply diagonalizing gates
        compiled_circuits = self.compile_circuits(circuits)

        # Send the batch of circuit objects using sampler.run
        sampler = LocalSampler()
        job = sampler.run(compiled_circuits)
        job_result = job.result()  # local operation, no API call here

        # Increment counter for number of executions of qubit device
        self._num_executions += 1

        # Compute statistics using the state and/or samples
        results = []
        self._metadatas = []

        for circuit, quasi_dist in zip(circuits, job_result.quasi_dists):
            # Process quasi-distribution into expected numerical result
            res = self._process_batch_execute_result(circuit, quasi_dist)
            results.append(res)

            # Construct metadata
            metadata = {
                "result_object": job_result,
                "num_measurements": self._num_executions,
            }
            self._metadatas.append(metadata)

        # Update tracker
        if self.tracker.active:
            self.tracker.update(batches=1, batch_len=n_circuits)
            self.tracker.record()

        if n_original_circuits != n_circuits:
            self._n_circuits = n_circuits
            self._n_original_circuits = n_original_circuits
            results = self._vector_results(results)

        return results

    def post_process(self, *args) -> Tuple[Any, List[dict]]:
        results = args[1]
        metadatas = self._metadatas.copy()
        self._metadatas = None
        return results, metadatas

    def post_process_all(self, *args) -> Tuple[Any, List[dict]]:
        # Dummy method for local Sampler, redirects to `post_process`
        return self.post_process(*args)
