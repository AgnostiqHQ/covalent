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

""""
Pennylane-Qiskit device that uses the Qiskit Runtime `Sampler` primitive
"""

from typing import List, Union

import pennylane
from qiskit_ibm_runtime import Sampler

from .devices_base import QiskitSamplerDevice
from .sessions import get_cached_session
from .utils import extract_options


class QiskitRuntimeSampler(QiskitSamplerDevice):
    """
    Pennylane device that runs circuits with Qiskit Runtime's `Sampler`
    """

    short_name = "sampler"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        wires: int,
        shots: int,
        backend_name: str,
        max_time: Union[int, str],
        options: dict,
        service_init_kwargs: dict,
    ):

        _options = extract_options(options)
        _options.execution.shots = shots
        self.options = _options
        self.max_time = max_time

        super().__init__(
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            service_init_kwargs=service_init_kwargs,
        )

    def batch_execute(self, circuits, timeout: int = None):
        # pylint: disable=missing-function-docstring

        n_original_circuits = len(circuits)
        circuits = self.broadcast_tapes(circuits)

        # This flag distinguishes vector inputs
        vector_input = (n_original_circuits != len(circuits))

        # Create circuit objects and apply diagonalizing gates
        compiled_circuits = self.compile_circuits(circuits)

        # Send the batch of circuit objects to Qiskit Runtime using sampler.run
        max_time = timeout or self.max_time
        with get_cached_session(self.service, self.backend, max_time) as session:
            sampler = Sampler(session=session, options=self.options)
            job = sampler.run(compiled_circuits)

        # Increment counter for number of executions of qubit device
        self._num_executions += 1

        # Adjust for active return status
        # Pack as list to satisfy expected `qml.execute` output in usual pipeline
        if not pennylane.active_return():
            jobs = [[job] for _ in circuits]
        else:
            jobs = [job] * len(circuits)

        # Add another "dimension" for unpacking in Pennylane `cache_execute`
        return [jobs] if vector_input else jobs

    def post_process(self, *args) -> List[dict]:
        # pylint: disable=too-many-locals

        circuits, jobs = args[:2]
        n_original_circuits = len(circuits)
        circuits = self.broadcast_tapes(circuits)  # also necessary for the `for` loop below

        # This flag distinguishes vector inputs
        vector_input = (n_original_circuits != len(circuits))

        # NOTE: the entries all point to the same object (see `self.batch_execute`)
        # instead of predicting shape, recursive unpack until nearest non-list element
        job = jobs[0]
        while isinstance(job, list):
            job = job[0]

        job_result = job.result()  # blocking call

        # Compute statistics using the state and/or samples
        results = []
        metadatas = []

        for i, circuit in enumerate(circuits):
            quasi_dist = job_result.quasi_dists[i]
            job_metadata = job_result.metadata[i]

            # Update tracker and process quasi-distribution into expected result
            res = self._process_batch_execute_result(circuit, quasi_dist)
            results.append(res)

            # Construct metadata
            metadata = {
                "result_object": job_result,
                "num_measurements": self._num_executions,
            }
            metadata.update(**job_metadata)
            metadatas.append(metadata)

        # Update tracker
        if self.tracker.active:
            self.tracker.update(batches=1, batch_len=len(circuits))
            self.tracker.record()

        # Wrap in outer list for vector inputs
        if vector_input:
            return [pennylane.numpy.asarray(results)], metadatas

        return results, metadatas
