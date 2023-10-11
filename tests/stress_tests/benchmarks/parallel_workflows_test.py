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

import secrets
import tempfile

import pytest

import covalent as ct
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_parallel_fileio_test(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def create_delete_tempfile():
        fp = tempfile.NamedTemporaryFile(delete=True)
        # thousand lines per file
        for i in range(1000):
            fp.write(secrets.token_bytes(16384))
        fp.close()

    @ct.lattice
    def parallel_fileio(N: int):
        for i in range(N):
            create_delete_tempfile()

    result, status = run_benchmark(iteration, parallel_fileio, *[50])
    logger.debug(result.dict())

    assert status == Status("COMPLETED")
