# Copyright 2021 Agnostiq Inc.
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

import platform

from pydantic import BaseModel


class PlatformMetadata(BaseModel):
    """Information about the platform used to run the benchmarks"""

    arch: str = platform.architecture()
    system: str = platform.system()
    machine: str = platform.machine()
    os: str = platform.node()
    python_version: str = platform.python_version()


class PerformanceMetrics(BaseModel):
    """Performance metrics to be gathered"""

    workflow_runtime: float
    covalent_runtime: float
    covalent_speedup: float
    covalent_overhead: float
    covalent_disk_io_time: float = 0.0
    covalent_network_io_time: float = 0.0
    covalent_fraction_disk_io: float = 0.0
    covalent_fraction_idle: float = 0.0
    covalent_fraction_user_mode: float = 0.0
    covalent_fraction_system_mode: float = 0.0
    covalent_dispatch_latency: float = 0.0
    covalent_dispatch_throughput: float = 0.0
    covalent_total_db_reads: float = 0.0
    covalent_total_db_writes: float = 0.0
    covalent_electron_throughput: float = 0.0
    covalent_electron_latency: float = 0.0


class WorkflowBenchmarkResult(BaseModel):
    """Base object representing the results from a single workflow benchmark run"""

    run_id: int
    workflow_name: str
    metadata: PlatformMetadata = PlatformMetadata()
    metrics: PerformanceMetrics
