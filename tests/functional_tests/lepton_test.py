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

"""Lepton functional tests."""

import os
from pathlib import Path

import covalent as ct
from covalent._results_manager import results_manager as rm
from covalent import DepsBash, DepsPip, DepsCall

deps_bash = DepsBash(["whoami"])
deps_pip = DepsPip(packages=["cloudpickle==2.0.0"])
call_before = DepsCall(deps_bash)
call_after = DepsCall(deps_bash)

@ct.leptons.bash(
    executor="local",
    display_name="debug",
    call_before=call_before,
    call_after=call_after,
    deps_bash=deps_bash,
    deps_pip=deps_pip
)
def task(x):
    return f"echo {x} > /tmp/debug.txt"


@ct.lattice
def workflow():
    task(5)


def test_bash_decorator():
    dispatch_id = ct.dispatch(workflow)()
    ct.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    file = Path("/tmp/debug.txt")
    assert file.is_file()

    with open("/tmp/debug.txt", "r") as f:
        result = int(f.readline().strip())
        assert result == 5

    os.remove("/tmp/debug.txt")
