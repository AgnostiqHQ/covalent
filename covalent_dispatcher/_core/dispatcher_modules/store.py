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

"""
Simple Key-Value store base
"""


class _KeyValueBase:
    async def get(self, key):
        raise NotImplementedError

    async def insert(self, key, val):
        raise NotImplementedError

    async def belongs(self, key):
        raise NotImplementedError

    async def remove(self, key):
        raise NotImplementedError

    async def increment(self, key: str, delta: int) -> int:
        """Increments value for `key` by amount `delta`

        Parameters:
            key: the value to change
            delta: the amount to change (can be negative)
        Returns:
            The new value
        """

        raise NotImplementedError


class _DictStore(_KeyValueBase):
    def __init__(self):
        self._store = {}

    async def get(self, key):
        return self._store[key]

    async def insert(self, key, val):
        self._store[key] = val

    async def belongs(self, key):
        return key in self._store

    async def remove(self, key):
        del self._store[key]

    async def increment(self, key, delta: int):
        self._store[key] += delta
        return self._store[key]
