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
