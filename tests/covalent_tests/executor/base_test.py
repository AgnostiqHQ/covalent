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

"""Tests for the Covalent executor base module."""

import os
import tempfile

from covalent.executor import BaseExecutor


class MockExecutor(BaseExecutor):
    def execute(self):
        pass


def test_write_streams_to_file(mocker):
    """Test write log streams to file method in BaseExecutor via LocalExecutor."""

    me = MockExecutor()

    # Case 1 - Check that relative log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = "relative.log"
        me.write_streams_to_file(stream_strings=["relative"], filepaths=[tmp_file], dispatch_id="", results_dir=tmp_dir)
        assert "relative.log" in os.listdir(tmp_dir)
        
        with open(f"{tmp_dir}/relative.log") as f:
            lines = f.readlines()
        assert lines[0] == "relative"

    # Case 2 - Check that absolute log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = tempfile.NamedTemporaryFile()
        me.write_streams_to_file(stream_strings=["absolute"], filepaths=[tmp_file.name], dispatch_id="", results_dir=tmp_dir)
        assert os.path.isfile(tmp_file.name)
        
        with open(tmp_file.name) as f:
            lines = f.readlines()
        assert lines[0] == "absolute"

    # Case 3 - Check that relative log files that are written to are constructed in results directory specified in the covalent conf file when not explicitly specified.
    with tempfile.TemporaryDirectory() as tmp_dir:
        mocker.patch('covalent.executor.base.get_config', return_value=tmp_dir)
        tmp_file = "relative.log"
        me.write_streams_to_file(stream_strings=["default"], filepaths=[tmp_file], dispatch_id="")
        assert "relative.log" in os.listdir(tmp_dir)
        
        with open(f"{tmp_dir}/relative.log") as f:
            lines = f.readlines()
        assert lines[0] == "default"
