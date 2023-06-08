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

"""Pennylane-Qiskit devices to Quantum Electrons"""
from typing import Any, List, Tuple, Union

import pennylane
from qiskit.compiler import transpile
from qiskit.primitives import Sampler as LocalSampler
from qiskit_ibm_runtime import Sampler

from .devices_base import QiskitSamplerDevice
from .sessions import get_cached_session
from .utils import extract_options


class QiskitLocalSampler(QiskitSamplerDevice):
    """
    Pennylane device that runs circuits using the local `qiskit.primitives.Sampler`
    """

    short_name = "local_sampler"

    def __init__(self, wires: int, shots: int, **_):

        self.circuit = None
        self.transpile_args = {}

        QiskitSamplerDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name="None",
            service_init_kwargs={},
        )

    def batch_execute(self, circuits):
        jobs = []
        sampler = LocalSampler()
        for circuit in circuits:
            tapes = self.broadcast_tapes([circuit])
            compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
            job = sampler.run(compiled_circuits)
            jobs.append(job)

        return [[job.result()] for job in jobs]

    def compile(self):
        """
        Override original method from `pennylane_qiskit.qiskit_device.QiskitDevice`
        to always use a `None` compile backend
        """
        return transpile(self._circuit, backend=None, **self.transpile_args)


class QiskitRuntimeSampler(QiskitSamplerDevice):
    """
    Pennylane device that runs circuits with Qiskit Runtime's `Sampler`
    """

    short_name = "sampler"

    def __init__(
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

        QiskitSamplerDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            service_init_kwargs=service_init_kwargs,
        )

    def batch_execute(self, circuits):

        with get_cached_session(  # pylint: disable=not-context-manager
            self.service,
            self.backend,
            self.max_time
        ) as session:

            sampler = Sampler(session=session, options=self.options)
            jobs = []
            for circuit in circuits:
                tapes = self.broadcast_tapes([circuit])
                compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
                job = sampler.run(compiled_circuits)
                jobs.append(job)

        if not pennylane.active_return():
            jobs = [[job] for job in jobs]

        return jobs

    def post_process(self, qscripts_list, results) -> Tuple[List[Any], List[dict]]:
        results = [[self.request_result(job)] for job in results]
        return super().post_process(qscripts_list, results)

    def request_result(self, job):
        """
        Required to handle the case when `pennylane.active_return() == False`
        """
        if not pennylane.active_return():
            job = job.pop()

        return job.result()
