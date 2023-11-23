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

from typing import Union

from pydantic import field_validator

from ...executor.qbase import (
    BaseProcessPoolQExecutor,
    BaseQExecutor,
    BaseThreadPoolQExecutor,
    SyncBaseQExecutor,
)

SIMULATOR_DEVICES = [
    "default.qubit",
    "default.qubit.autograd",
    "default.qubit.jax",
    "default.qubit.tf",
    "default.qubit.torch",
    "default.gaussian",
    "lightning.qubit",
]


class Simulator(BaseQExecutor):
    """
    A quantum executor that uses the specified Pennylane device to execute circuits.
    Parallelizes circuit execution on the specified `device` using either threads
    or processes.

    Keyword Args:
        device: A valid string corresponding to a Pennylane device. Simulation-based
            devices (e.g. "default.qubit" and "lightning.qubit") are recommended.
            Defaults to "default.qubit" or "default.gaussian" depending on the
            decorated QNode's device.
        parallel: The type of parallelism to use. Valid values are "thread" and
            "process". Passing any other value will result in synchronous execution.
            Defaults to "thread".
        workers: The number of threads or processes to use. Defaults to 10.
        shots: The number of shots to use for the execution device. Overrides the
            :code:`shots` value from the original device if set to :code:`None` or
            a positive :code:`int`. The shots setting from the original device is
            is used by default.
    """

    device: str = "default.qubit"
    parallel: Union[bool, str] = "thread"
    workers: int = 10

    @field_validator("device")
    def validate_device(cls, device):  # pylint: disable=no-self-argument
        """
        Check that the `device` attribute is NOT a provider or hardware device.
        """
        if device not in SIMULATOR_DEVICES:
            valid_devices = ", ".join(SIMULATOR_DEVICES[::-1] + [f"or {SIMULATOR_DEVICES[-1]}"])
            raise ValueError(f"Simulator device must be {valid_devices}.")
        return device

    def batch_submit(self, qscripts_list):
        # Defer to original QNode's device type in special cases.
        if self.qelectron_info.device_name in ["default.gaussian"]:
            device = self.qelectron_info.device_name
        else:
            device = self.device

        # Select backend batching the chosen method of parallelism.
        if self.parallel == "process":
            self._backend = BaseProcessPoolQExecutor(num_processes=self.workers, device=device)
        elif self.parallel == "thread":
            self._backend = BaseThreadPoolQExecutor(num_threads=self.workers, device=device)
        else:
            self._backend = SyncBaseQExecutor(device=device)

        # Pass on server-set settings from original device.
        updates = {"device_name": device, "device_shots": self.override_shots}
        self._backend.qelectron_info = self.qelectron_info.copy(update=updates)
        self._backend.qnode_specs = self.qnode_specs.copy()

        return self._backend.batch_submit(qscripts_list)

    def batch_get_results(self, futures_list):
        return self._backend.batch_get_results(futures_list)

    _backend: BaseQExecutor = None
