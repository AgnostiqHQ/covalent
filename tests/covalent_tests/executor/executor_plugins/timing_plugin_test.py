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


"""Unit tests for the TimingPlugin class."""


from covalent.executor.executor_plugins.timing_plugin import (
    _EXECUTOR_PLUGIN_DEFAULTS,
    EXECUTOR_PLUGIN_NAME,
    TimingExecutor,
)


def test_init():
    """Test initialization of TimingPlugin."""

    timing_plugin = TimingExecutor("mock-path")
    assert EXECUTOR_PLUGIN_NAME == "TimingExecutor"
    assert _EXECUTOR_PLUGIN_DEFAULTS == {"timing_filepath": ""}
    assert timing_plugin.timing_filepath.endswith("mock-path")


def test_run(mocker):
    """Test the run method of TimingPlugin."""

    mocker.patch(
        "covalent.executor.executor_plugins.timing_plugin.time.process_time", side_effect=[1, 2]
    )

    timing_plugin = TimingExecutor("/tmp/mock_timing_file.log")

    def mock_func(x):
        return x + 2

    res = timing_plugin.run(mock_func, [1], {}, {"node_id": 1, "dispatch_id": 1})
    assert res == 3

    with open(timing_plugin.timing_filepath, "r") as f:
        timing_file = f.read()

    assert timing_file == "Node 1 in dispatch 1 took 1s of CPU time."
