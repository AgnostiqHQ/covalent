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
Utils for the data service
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

# Worker thread for Datastore I/O Clamp this threadpool to one
# thread because Sqlite only supports a single writer.
dm_pool = ThreadPoolExecutor(max_workers=1)


def run_in_executor(func, *args) -> asyncio.Future:
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(dm_pool, func, *args)
