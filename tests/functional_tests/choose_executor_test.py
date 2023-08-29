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

"""Functional tests for selecting executor"""


import covalent as ct


def test_using_executor_names():
    """Test that all loaded executors can be used in a simple electron."""

    executor_name = "local"

    @ct.electron(executor=executor_name)
    def passthrough(x):
        return x

    @ct.lattice()
    def workflow(y):
        return passthrough(x=y)

    dispatch_id = ct.dispatch(workflow)(y="input")
    output = ct.get_result(dispatch_id, wait=True)

    assert output.result == "input"


def test_using_executor_classes():
    """Test creating executor objects and using them in a simple electron."""

    executor = ct.executor.LocalExecutor()

    @ct.electron(executor=executor)
    def passthrough(x):
        return x

    @ct.lattice
    def workflow(y):
        return passthrough(x=y)

    dispatch_id = ct.dispatch(workflow)(y="input")
    output = ct.get_result(dispatch_id, wait=True)

    assert output.result == "input"
