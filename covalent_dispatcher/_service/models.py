# Copyright 2021 Agnostiq Inc.
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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from enum import Enum

# # Copied from _dal
# RESULT_ASSET_KEYS = {
#     "inputs",
#     "result",
#     "error",
# }

# # Copied from _dal
# LATTICE_ASSET_KEYS = {
#     "workflow_function",
#     "workflow_function_string",
#     "__doc__",
#     "named_args",
#     "named_kwargs",
#     "cova_imports",
#     "lattice_imports",
#     # metadata
#     "executor_data",
#     "workflow_executor_data",
#     "deps",
#     "call_before",
#     "call_after",
# }

# # Copied from _dal
# ELECTRON_ASSET_KEYS = {
#     "function",
#     "function_string",
#     "output",
#     "value",
#     "error",
#     "stdout",
#     "stderr",
#     # electron metadata
#     "deps",
#     "call_before",
#     "call_after",
# }


class DispatchAssetKey(str, Enum):
    inputs = "inputs"
    result = "result"
    error = "error"


class LatticeAssetKey(str, Enum):
    workflow_function = "workflow_function"
    workflow_function_string = "workflow_function_string"
    doc = "__doc__"
    named_args = "named_args"
    named_kwargs = "named_kwargs"
    deps = "deps"
    call_before = "call_before"
    call_after = "call_after"


class ElectronAssetKey(str, Enum):
    function = "function"
    function_string = "function_string"
    output = "output"
    value = "value"
    deps = "deps"
    error = "error"
    stdout = "stdout"
    stderr = "stderr"
    call_before = "call_before"
    call_after = "call_after"
