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
