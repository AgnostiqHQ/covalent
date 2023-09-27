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

# pylint: disable=too-few-public-methods

import random

from .base import BaseQSelector


class RandomSelector(BaseQSelector):
    """
    A selector that randomly selects an executor.
    """

    name: str = "random"

    def selector_function(self, qscript, executors):
        return random.choice(executors)


class CyclicSelector(BaseQSelector):
    """
    A selector that cycles in order through the available executors.
    """

    name: str = "cyclic"

    _counter: int = 0

    def selector_function(self, qscript, executors):
        executor = executors[self._counter % len(executors)]
        self._counter += 1
        return executor


selector_map = {
    "cyclic": CyclicSelector,
    "random": RandomSelector,
}
