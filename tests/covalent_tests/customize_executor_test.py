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

"""Unit test for customizing the local executor."""

import sys
import tempfile
from pathlib import Path

import covalent as ct


@ct.electron
def task(x):
    print(f"stdout: {x}")
    print("Error!", file=sys.stderr)
    return x


@ct.lattice
def workflow(x):
    return task(x)


def test_logs_placed_correctly():
    """Test log files are placed in the correct locations."""

    # Test with absolute paths
    with tempfile.TemporaryDirectory() as tmpdir:
        ct.set_config(
            {
                "executors.local.log_stdout": f"{tmpdir}/stdout.log",
                "executors.local.log_stderr": f"{tmpdir}/stderr.log",
            }
        )

        workflow.dispatch_sync("absolute")

        # Assert files were created
        assert Path(f"{tmpdir}/stdout.log").exists()
        assert Path(f"{tmpdir}/stderr.log").exists()

        # Check file contents


#        with open(f"{tmpdir}/stdout.log") as f:
#            assert len(f.readlines()) == 1
#            assert f.readlines()[0] == "stdout: absolute"

#        with open(f"{tmpdir}/stderr.log") as f:
#            assert len(f.readlines()) == 1
#            assert f.readlines()[0] == "Error!"
