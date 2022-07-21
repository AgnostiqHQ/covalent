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

"""Tests for Covalent local executor."""

import tempfile
from functools import partial

import covalent as ct
from covalent._workflow.transport import TransportableObject
from covalent.executor.executor_plugins.local import LocalExecutor
from covalent_dispatcher.utils import wrapper_fn


def test_local_executor_passes_results_dir(mocker):
    """Test that the local executor calls the stream writing function with the results directory specified."""

    with tempfile.TemporaryDirectory() as tmp_dir:

        @ct.electron
        def simple_task(x, y):
            print(x, y)
            return x, y

        mocked_function = mocker.patch(
            "covalent.executor.executor_plugins.local.LocalExecutor.write_streams_to_file"
        )
        le = LocalExecutor()
        assembled_fn = partial(wrapper_fn, TransportableObject(simple_task), [], [])
        le.execute(
            function=assembled_fn,
            args={"x": TransportableObject(1)},
            kwargs={"y": TransportableObject(2)},
            dispatch_id=-1,
            results_dir=tmp_dir,
            node_id=0,
        )
        mocked_function.assert_called_once()


def test_local_executor_json_serialization():
    import json

    le = LocalExecutor(log_stdout="/dev/null")
    json_le = json.dumps(le.to_dict())
    le_new = LocalExecutor().from_dict(json.loads(json_le))
    assert le.__dict__ == le_new.__dict__


def test_wrapper_fn_calldep_retval_injection():
    """Test injecting calldep return values into main task"""

    def f(x=0, y=0):
        return x + y

    def identity(y):
        return y

    serialized_fn = TransportableObject(f)
    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")
    call_before = [calldep.apply()]
    args = []
    kwargs = {"x": TransportableObject(2)}

    output = wrapper_fn(serialized_fn, call_before, [], *args, **kwargs)

    assert output.get_deserialized() == 7


def test_local_executor_run():
    def f(x):
        return x**2

    le = LocalExecutor()
    args = [5]
    kwargs = {}
    assert le.run(f, args, kwargs) == 25
