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

"""Test the deps functionality."""

from pathlib import Path

import numpy

import covalent as ct
from covalent import DepsBash, DepsCall, DepsPip


def test_deps_workflow():
    """Test the deps functionality."""

    deps_pip = DepsPip(packages=["numpy==1.23.1"])
    deps_bash = DepsBash(commands=["echo $HOME >> /tmp/deps_bash_test.txt"])

    def deps_call():
        Path("/tmp/deps_bash_test.txt").unlink()

    @ct.electron(
        call_before=[deps_pip, deps_bash],
        call_after=[DepsCall(deps_call)],
    )
    def get_deps_results():
        results = []
        with open("/tmp/deps_bash_test.txt", "r") as f:
            results.append(f.read())
        results.append(numpy.sum(numpy.identity(3)))
        return results

    @ct.lattice
    def workflow():
        return get_deps_results()

    # Dispatch the workflow
    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    assert int(res.result[1]) == 3
    assert res.status == "COMPLETED"
