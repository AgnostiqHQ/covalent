# Copyright 2023 Agnostiq Inc.
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

"""Test the deps functionality."""

from pathlib import Path

import numpy
import pytest

import covalent as ct
from covalent import DepsBash, DepsCall, DepsPip


@pytest.mark.skip(reason="temp skip test")
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
