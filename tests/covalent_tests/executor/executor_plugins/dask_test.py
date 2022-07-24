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

"""Tests for Covalent dask executor."""

import asyncio

import pytest


def test_dask_executor_init(mocker):
    """Test dask executor constructor"""

    from covalent.executor import DaskExecutor

    de = DaskExecutor("127.0.0.1")

    assert de.scheduler_address == "127.0.0.1"


def test_dask_executor_run():
    """Test run method for Dask executor"""

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    dask_exec = DaskExecutor(cluster.scheduler_address)

    def f(x, y):
        return x, y

    args = [5]
    kwargs = {"y": 7}
    assert asyncio.run(dask_exec.run(f, args, kwargs)) == (5, 7)
