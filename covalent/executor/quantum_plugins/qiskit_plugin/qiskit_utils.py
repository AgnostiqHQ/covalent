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
