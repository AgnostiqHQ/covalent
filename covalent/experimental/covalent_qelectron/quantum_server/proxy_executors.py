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

from covalent.executor import _qexecutor_manager

from ..executors.base import *
from ..executors.clusters import *
from ..executors.plugins import *

for qexecutor_cls in _qexecutor_manager.executor_plugins_map.values():
    globals()[qexecutor_cls.__name__] = qexecutor_cls

# Ways to add new methods/attributes to the executor classes:

# 1. Inherit from the class and add new methods/attributes:

# class Simulator(Simulator):
#     def my_method(self):
#         print("Hello World")

# 2. Assign directly to the class, but it also modifies
# the original class, so it's better for remote server case:

# Simulator.my_method = lambda self: print("Hello World")
