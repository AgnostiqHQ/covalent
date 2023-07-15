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

from typing import Any, List, Union

import pennylane as qml
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
            service_init_kwargs=service_init_kwargs,
        )

    def dummy_result(self, n_circuits: int) -> Union[Any, List[Any]]:
        """
        Returns a dummy result to satisfy the expected `qml.execute` output.
        This allows async submission to proceed without waiting for the job result.
        """

        # Pack as list to satisfy expected `qml.execute` output in usual pipeline
        if not self.pennylane_active_return:
            dummy_result = [[self.asarray(0.)]] * n_circuits
        else:
            dummy_result = [self.asarray(0.)] * n_circuits

        # Add another "dimension" for unpacking in Pennylane `cache_execute`
        return [dummy_result] if self._vector_input else dummy_result

    def batch_execute(self, circuits, timeout: int = None):
        """
        Submit a batch of circuits to IBM Qiskit Runtime for execution.
        """

        n_original_circuits = len(circuits)
        circuits = self.broadcast_tapes(circuits)
        n_broadcasted_circuits = len(circuits)

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
        self._vector_input = n_original_circuits != n_broadcasted_circuits

        # Return a dummy result and proceed to subsequent submissions.
        return self.dummy_result(n_broadcasted_circuits)

    def post_process(self, *args):
        """
        Post-process a single circuit result.
        """

        post_processed_results = []
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
            post_processed_results.append(res)

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
        post_processed_results = self.re_execute([tape], post_processed_results)

        # Wrap in outer list for vector inputs
        if self._vector_input:
            return [self.asarray(post_processed_results)], metadatas

        return post_processed_results, metadatas

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
        post_processed_results = []
        metadatas = []

        for i, circuit in enumerate(self._active_circuits):
            quasi_dist = job_result.quasi_dists[i]

            # Update tracker and process quasi-distribution into expected result
            res = self._process_batch_execute_result(circuit, quasi_dist)
            post_processed_results.append(res)

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
        post_processed_results = self.re_execute(tapes, post_processed_results)

        # Wrap in outer list for vector inputs
        if self._vector_input:
            return [self.asarray(post_processed_results)], metadatas

        return post_processed_results, metadatas

    def re_execute(self, tapes, results):
        """
        Executes circuits on a dummy device that returns the provided result.

        This is necessary for the raw output from `post_process` to be handled
        as if it came from `batch_execute`.
        """
        dev = _PostProcessDevice(self.wires, results)
        return qml.execute(tapes, dev, None)


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
            max_time=1,
            single_job=False,
            options={},
            service_init_kwargs={}
        )

        self._results = results

    def batch_execute(self, *_, **__):
        """
        Override to return expected result.
        """
        return self._results
