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

from pathlib import Path

import pytest

import covalent as ct
from covalent import DepsBash, DepsCall, DepsPip
from covalent._file_transfer.enums import Order
from covalent._results_manager import results_manager as rm


def test_bash_decorator():
    def call_hook():
        return None

    deps_bash = DepsBash(["whoami"])
    deps_pip = DepsPip(packages=["cloudpickle==2.0.0"])
    call_before = DepsCall(call_hook)
    call_after = DepsCall(call_hook)
    source_file = Path("/tmp/src.txt")
    dest_file = Path("/tmp/dest.txt")
    dest_file2 = Path("/tmp/dest2.txt")

    echofile = Path("/tmp/debug.txt")
    echofile2 = Path("/tmp/debug2.txt")

    @ct.leptons.bash(
        executor="local",
        display_name="debug",
        call_before=call_before,
        call_after=call_after,
        deps_bash=deps_bash,
        deps_pip=deps_pip,
        files=[ct.fs.FileTransfer(str(source_file), str(dest_file), order=Order.BEFORE)],
    )
    def task(x):
        return f"echo {x} > {str(echofile)}"

    def task2(x):
        return f"echo {x} > {str(echofile2)}"

    @ct.lattice
    def workflow():
        task(5)

        ct.leptons.bash(
            task2,
            files=[ct.fs.FileTransfer(str(source_file), str(dest_file2), order=Order.AFTER)],
            deps_pip=["cloudpickle==2.0.0"],
        )(3)

    source_file.touch()

    dispatch_id = ct.dispatch(workflow)()
    ct.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert echofile.is_file()

    with open(str(echofile), "r") as f:
        result = int(f.readline().strip())
        assert result == 5

    assert echofile2.is_file()

    with open(str(echofile2), "r") as f:
        result = int(f.readline().strip())
        assert result == 3

    echofile.unlink()
    echofile2.unlink()
    source_file.unlink()
    dest_file.unlink()
    dest_file2.unlink()


def test_call_dep_retvals_in_lepton():
    """
    Test DepsCall retval_keyword behavior in electrons which currently is to raise an error if any retval_key is added.
    """

    echofile = Path("/tmp/debug.txt")

    def call_dep_hook():
        return 123

    @ct.leptons.bash(
        executor="local",
        display_name="file_transfer_lepton",
        call_before=[ct.DepsCall(call_dep_hook, retval_keyword="call_dep_hook")],
    )
    def file_transfer(call_dep_hook=None):
        return f"echo {call_dep_hook} > {str(echofile)}"

    @ct.lattice
    def ft_workflow():
        return file_transfer()

    with pytest.raises(Exception):
        dispatch_id = ct.dispatch(ft_workflow)()
        ct.get_result(dispatch_id, wait=True)
        rm._delete_result(dispatch_id)
