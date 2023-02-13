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

"""
Testing whether Triggers functionality works as expected
"""

import time
from pathlib import Path

import covalent as ct
from covalent.triggers import DirTrigger


def test_dir_trigger():
    read_file_path = str(Path("dir_tr_read.txt").resolve())
    write_file_path = str(Path("dir_tr_write.txt").resolve())

    print(read_file_path)

    dir_trigger = DirTrigger(read_file_path, event_names="modified")

    @ct.lattice(triggers=dir_trigger)
    @ct.electron
    def dir_workflow():
        with open(read_file_path, "r") as f:
            numbers = f.readlines()

        total_sum = sum(int(n) for n in numbers)

        with open(write_file_path, "a") as f:
            f.write(f"{total_sum}\n")

    with open(read_file_path, "a") as f:
        f.write("0\n")

    ct.dispatch(dir_workflow)()

    expected_sums = [0]
    for i in range(1, 5):
        expected_sums.append(i + sum(expected_sums))

        with open(read_file_path, "a") as f:
            f.write(f"{i}\n")

        time.sleep(2)

        with open(write_file_path, "r") as f:
            actual_sums = f.readlines()

        actual_sums = [int(n) for n in actual_sums]

    assert expected_sums == actual_sums


def test_time_trigger():
    pass
