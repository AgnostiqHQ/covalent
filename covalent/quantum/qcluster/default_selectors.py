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
