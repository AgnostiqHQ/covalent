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

import pennylane as qml
from qiskit_ibm_runtime import Sampler

from .devices_base import QiskitSamplerDevice
from .sessions import get_cached_session
from .utils import extract_options


def _post_process_device(wires):

    class _PostProcessDevice(QiskitRuntimeSampler):
        # pylint: disable=too-few-public-methods

        results = None

        def batch_execute(self, *_, **__):
            """
            Override to return expected result.
            """
            return self.results

    return _PostProcessDevice(
        wires=wires,
        shots=1,
        backend_name="",
        max_time=1,
        options={},
        service_init_kwargs={}
    )


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

        if options:
            _options = extract_options(options)
            _options.execution.shots = shots
        else:
            _options = None

        self.options = _options
        self.max_time = max_time

        self._active_job = None
        self._active_circuits = None
        self._vector_input = False

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

        # Create circuit objects and apply diagonalizing gates
        compiled_circuits = self.compile_circuits(circuits)
        self._active_circuits = [circuit.copy() for circuit in circuits]

        # Send the batch of circuit objects to Qiskit Runtime using sampler.run
        max_time = timeout or self.max_time
        with get_cached_session(self.service, self.backend, max_time) as session:
            sampler = Sampler(session=session, options=self.options)
            job = sampler.run(compiled_circuits)
        self._active_job = job

        # Adjust for active return status
        # Pack as list to satisfy expected `qml.execute` output in usual pipeline
        if not self.pennylane_active_return:
            dummy_result = [[self._asarray(0.)]] * len(circuits)
        else:
            dummy_result = [self._asarray(0.)] * len(circuits)

        # This flag distinguishes vector inputs from gradient computations
        self._vector_input = (n_original_circuits != len(circuits))

        # Add another "dimension" for unpacking in Pennylane `cache_execute`
        results = [dummy_result] if self._vector_input else dummy_result
        return results

    def post_process(self, *args) -> List[dict]:
        # pylint: disable=too-many-locals

        # Unpack args, ignore dummy result
        circuits = self._active_circuits
        self._active_circuits = None

        # Get active jobs from attribute and reset
        job = self._active_job
        self._active_job = None

        # Blocking call to retrieve job result
        job_result = job.result()

        # Increment counter for number of executions of qubit device
        self._num_executions += 1

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
        if self._vector_input:
            return [self._asarray(results)], metadatas

        # Re-execute with a dummy device to get correct result
        results = self.re_execute(args[0], results)

        return results, metadatas

    def re_execute(self, circuits, results):
        """
        Executes circuits on a dummy device that returns the provided result.

        This is necessary for the raw output from `post_process` to be handled
        as if it came from `batch_execute`.
        """
        dev = _post_process_device(self.wires)
        dev.results = results
        return qml.execute(circuits, dev, None)
