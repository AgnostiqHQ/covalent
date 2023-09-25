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
Pennylane-Qiskit device that uses the Qiskit Runtime `Sampler` primitive
"""

from typing import Any, List, Sequence, Union

import pennylane as qml
from devices_base import QiskitSamplerDevice
from qiskit_ibm_runtime import Sampler
from qiskit_utils import extract_options
from sessions import get_cached_session


class QiskitRuntimeSampler(QiskitSamplerDevice):
    """
    Pennylane device that runs circuits with Qiskit Runtime's `Sampler`
    """

    short_name = "sampler"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        wires: int,
        shots: Union[None, int, Sequence[int], Sequence[Union[int, Sequence[int]]]],
        backend_name: str,
        local_transpile: bool,
        max_time: Union[int, str],
        single_job: bool,
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
        self.single_job = single_job

        # These attributes are shared across `batch_execute` and `post_process`
        self._active_jobs = []
        self._active_circuits = []
        self._vector_input = False

        super().__init__(
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            local_transpile=local_transpile,
            service_init_kwargs=service_init_kwargs,
        )

    def batch_execute(self, circuits, timeout: int = None):
        """
        Submit a batch of circuits to IBM Qiskit Runtime for execution.
        """

        self._n_original_circuits = len(circuits)
        circuits = self.broadcast_tapes(circuits)
        self._n_circuits = len(circuits)

        # Create circuit objects and apply diagonalizing gates
        compiled_circuits = self.compile_circuits(circuits)
        self._active_circuits = [circuit.copy() for circuit in circuits]

        # Submit circuit objects to Qiskit Runtime
        max_time = timeout or self.max_time
        with get_cached_session(self.service, self.backend, max_time) as session:
            sampler = Sampler(session=session, options=self.options)

            if self.single_job:
                job = sampler.run(compiled_circuits)
                self._active_jobs.append(job)
            else:
                for compiled_circuit in compiled_circuits:
                    job = sampler.run(compiled_circuit)
                    self._active_jobs.append(job)

        # This flag distinguishes vector inputs from gradient computations
        self._vector_input = self._n_original_circuits != self._n_circuits

        # Return a dummy result and proceed to subsequent submissions.
        return self._dummy_result()

    def post_process(self, *args):
        """
        Post-process a single circuit result.
        """

        results = []
        metadatas = []
        for i, circuit in enumerate(self._active_circuits):
            # Get broadcasted circuit and active job
            circuit = self._active_circuits[i]
            job = self._active_jobs[i]

            # Blocking call to retrieve job result
            job_result = job.result()
            self._num_executions += 1

            # Extra metadata and quasi-distribution
            assert len(job_result.quasi_dists) == 1
            assert len(job_result.metadata) == 1
            quasi_dist = job_result.quasi_dists[0]

            # Post process the quasi-distribution into expected result
            res = self._process_batch_execute_result(circuit, quasi_dist)
            results.append(res)

            # Update metadata
            job_metadata = job_result.metadata[0]
            metadata = {
                "result_object": job_result,
                "num_measurements": self.num_executions,
            }
            metadata.update(**job_metadata)
            metadatas.append(metadata)

        # Update tracker
        if self.tracker.active:
            self.tracker.update(batches=len(self._active_circuits), batch_len=1)
            self.tracker.record()

        # Reset active jobs and circuits
        self._active_jobs = []
        self._active_circuits = []

        # Re-execute original tape with a dummy device to get correct result
        tape = args[0]
        results = self._re_execute(self.broadcast_tapes([tape]), results)

        # Wrap in outer list for vector inputs
        if self._vector_input:
            results = self._vector_results(results)

        return results, metadatas

    def post_process_all(self, *args):
        """
        Post-process a batch of circuit results.
        """

        # Blocking call to retrieve job result
        job = self._active_jobs.pop()
        job_result = job.result()

        # Increment counter for number of executions of qubit device
        self._num_executions += 1

        # Compute statistics using the state and/or samples
        results = []
        metadatas = []

        for i, circuit in enumerate(self._active_circuits):
            quasi_dist = job_result.quasi_dists[i]

            # Update tracker and process quasi-distribution into expected result
            res = self._process_batch_execute_result(circuit, quasi_dist)
            results.append(res)

            # Construct metadata
            job_metadata = job_result.metadata[i]
            metadata = {
                "result_object": job_result,
                "num_measurements": self._num_executions,
            }
            metadata.update(**job_metadata)
            metadatas.append(metadata)

        # Update tracker
        if self.tracker.active:
            self.tracker.update(batches=1, batch_len=len(self._active_circuits))
            self.tracker.record()

        # Reset active jobs and circuits
        self._active_jobs = []
        self._active_circuits = []

        # Re-execute with a dummy device to get correct result
        tapes = args[0]
        results = self._re_execute(self.broadcast_tapes(tapes), results)

        # Wrap in outer list for vector inputs
        if self._vector_input:
            results = self._vector_results(results)

        return results, metadatas

    def _re_execute(self, tapes, results):
        """
        Executes circuits on a dummy device that returns the provided result.

        This is necessary for the raw output from `post_process` to be handled
        as if it came from `batch_execute`.
        """
        dev = _PostProcessDevice(self.wires, results)
        return qml.execute(tapes, dev, gradient_fn="best")

    def _dummy_result(self) -> Union[Any, List[Any]]:
        """
        Returns a dummy result to satisfy the expected `qml.execute` output.
        This allows async submission to proceed without waiting for the job result.
        """

        dummy_results = qml.numpy.zeros(self.vector_shape)

        if self.pennylane_active_return:
            dummy_results = list(dummy_results)

        if self.single_job and self._vector_input:
            if self.pennylane_active_return:
                return [[d] for d in dummy_results]
            return [[d] for d in list(dummy_results)]

        if self._vector_input:
            return [dummy_results]
        return [[d] for d in dummy_results]


class _PostProcessDevice(QiskitRuntimeSampler):
    """
    A copy of the QiskitRuntimeSampler class with a dummy `batch_execute` method
    that returns the assigned `results`.
    """

    def __init__(self, wires, results: Any):
        super().__init__(
            wires=wires,
            shots=1,
            backend_name="",
            local_transpile=False,
            max_time=1,
            single_job=False,
            options={},
            service_init_kwargs={},
        )

        self._results = results

    def batch_execute(self, *_, **__):
        """
        Override to return expected result.
        """
        return self._results
