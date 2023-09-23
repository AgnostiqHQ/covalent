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

"""
Utilities for Qiskit-based QElectron executors and devices
"""

from qiskit_ibm_runtime import Options


def extract_options(opts: dict) -> Options:
    """
    Construct a Qiskit `Options` object from the options dictionary
    """
    if isinstance(opts, tuple):
        opts = dict(opts)

    _options = Options()
    _options.optimization_level = opts.get("optimization_level", 3)
    _options.resilience_level = opts.get("resilience_level", 1)
    _options.max_execution_time = opts.get("max_execution_time", None)
    _options.transpilation = opts.get("transpilation", _options.transpilation)
    _options.resilience = opts.get("resilience", _options.resilience)
    _options.execution = opts.get("execution", _options.execution)
    _options.environment = opts.get("environment", _options.environment)
    _options.simulator = opts.get("simulator", _options.simulator)
    return _options
