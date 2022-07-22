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
Integration test for choosing executors.
"""

import pytest

import covalent as ct


def test_executors_exist():
    """Test that there is at least one executor loaded."""

    executor_list = ct.executor._executor_manager.list_executors(print_names=False)
    assert len(executor_list) > 0


def test_using_executor_names():
    """Test that all loaded executors can be used in a simple electron."""

    for executor_name in ["local", "dask"]:

        @ct.electron(executor=executor_name)
        def passthrough(x):
            return x

        @ct.lattice()
        def workflow(y):
            return passthrough(x=y)

        dispatch_id = ct.dispatch(workflow)(y="input")
        output = ct.get_result(dispatch_id, wait=True)

        assert output.result == "input"


@pytest.mark.skip(reason="Trying to pickle _asyncio.Task even though there is no such object")
def test_using_executor_classes():
    """Test creating executor objects and using them in a simple electron."""

    for executor in [ct.executor.LocalExecutor(), ct.executor.DaskExecutor()]:

        @ct.electron(executor=executor)
        def passthrough(x):
            return x

        @ct.lattice
        def workflow(y):
            return passthrough(x=y)

        dispatch_id = ct.dispatch(workflow)(y="input")
        output = ct.get_result(dispatch_id, wait=True)

        assert output.result == "input"
