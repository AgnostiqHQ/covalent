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
