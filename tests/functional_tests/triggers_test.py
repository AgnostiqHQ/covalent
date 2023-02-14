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
from covalent.triggers import DirTrigger, TimeTrigger


def test_dir_trigger():
    Path("./tr_read").mkdir(exist_ok=True)
    Path("./tr_write").mkdir(exist_ok=True)

    read_file_path = str(Path("./tr_read/trigger_read.txt").resolve())
    write_file_path = str(Path("./tr_write/trigger_write.txt").resolve())

    print(read_file_path)

    dir_trigger = DirTrigger(str(Path("./tr_read").resolve()), event_names="modified")

    @ct.lattice(triggers=dir_trigger)
    @ct.electron
    def dir_workflow():
        with open(read_file_path, "r") as f:
            numbers = f.readlines()

        total_sum = sum(int(n) for n in numbers)

        with open(write_file_path, "a") as f:
            f.write(f"{total_sum}\n")

    with open(read_file_path, "w") as f:
        f.write("0\n")

    dispatch_id = ct.dispatch(dir_workflow)()

    expected_sums = {1}
    net_sum = 0
    for i in range(1, 5):
        net_sum += i
        expected_sums.add(net_sum)

        with open(read_file_path, "a") as f:
            f.write(f"{i}\n")

        time.sleep(2)

        with open(write_file_path, "r") as f:
            actual_sums = f.readlines()

        actual_sums = {int(n) for n in actual_sums}

    ct.stop_triggers(dispatch_id)

    Path(read_file_path).unlink()
    Path("./tr_read").rmdir()
    Path(write_file_path).unlink()
    Path("./tr_write").rmdir()

    assert expected_sums == actual_sums


def test_time_trigger():
    Path("./tr_write").mkdir(exist_ok=True)
    write_file_path = str(Path("./tr_write/trigger_write.txt").resolve())

    time_trigger = TimeTrigger(time_gap=2)

    @ct.lattice(triggers=time_trigger)
    @ct.electron
    def time_workflow():
        with open(write_file_path, "r+") as f:
            last_val = int(f.readlines()[-1])
            f.write(f"{last_val * 2}\n")

    with open(write_file_path, "w") as f:
        f.write("2\n")

    dispatch_id = ct.dispatch(time_workflow)()

    expected_val = 32
    time.sleep(8)
    ct.stop_triggers(dispatch_id)
    time.sleep(2)

    with open(write_file_path, "r") as f:
        actual_val = int(f.readlines()[-1])

    Path(write_file_path).unlink()
    Path("./tr_write").rmdir()

    assert expected_val == actual_val
