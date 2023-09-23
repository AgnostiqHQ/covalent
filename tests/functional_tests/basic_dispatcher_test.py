# Copyright 2021 Agnostiq Inc.
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

from pathlib import Path

import pytest

import covalent as ct
from covalent._results_manager import results_manager as rm


def test_dispatcher_functional():
    # Dispatch after starting the dispatcher server.

    the_executor = ct.executor.LocalExecutor(
        log_stdout="/tmp/log_stdout.txt", log_stderr="/tmp/log_stderr.txt"
    )

    @ct.electron(executor=the_executor)
    def passthrough_a(input):
        print("passthrough_a")
        return f"a{input}"

    @ct.electron(executor=the_executor)
    def concatenator(input_a, input_b):
        print("concatenator")
        return f"{input_a}{input_b}"

    @ct.electron(executor=the_executor)
    def concatenator_dict(input_a, input_b):
        print("concatenator")
        return {"input": f"{input_a}{input_b}"}

    @ct.electron(executor=the_executor)
    def passthrough_b(input):
        print("passthrough_b")
        return f"b{input}"

    @ct.lattice
    def workflow(name):
        a = passthrough_a(input=name)
        b = passthrough_b(input=name)
        return concatenator(input_a=a, input_b=b)

    @ct.lattice
    def bad_workflow(name):
        a = passthrough_a(input=name)
        raise RuntimeError(f"byebye {input}")

    dispatch_id = ct.dispatch(workflow)(name="q")

    res = ct.get_result(dispatch_id, wait=True)
    output = res.result

    assert output == "aqbq"

    try:
        output = ct.dispatch(bad_workflow)("z")
    except Exception as ex:
        print(f"Exception thrown for dispatching bad workflow as {ex}.")
        output = "failed"

    rm._delete_result(dispatch_id)
    assert output == "failed"

    Path(the_executor.log_stdout).unlink(missing_ok=True)
    Path(the_executor.log_stderr).unlink(missing_ok=True)


@pytest.mark.skip(reason="results_dir is no longer used. This test should be removed soon.")
def test_results_dir_in_sublattice():
    # Test that a "non-standard" results_dir in a sublattice works.

    def square(x):
        return x * x

    lattice_square = ct.lattice(square, results_dir="/tmp/results")

    @ct.lattice
    def outer_lattice(y):
        return ct.electron(lattice_square)(x=y)

    dispatch_id = ct.dispatch(outer_lattice)(y=5)
    result_object = ct.get_result(dispatch_id, wait=True)
    output = result_object.result

    rm._delete_result(dispatch_id, results_dir="/tmp/results")

    assert result_object.error == ""
    assert result_object.status == result_object.COMPLETED

    assert output == 25

    rm._delete_result(
        dispatch_id=dispatch_id, results_dir="/tmp/results", remove_parent_directory=True
    )
