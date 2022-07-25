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

from pathlib import Path

import covalent as ct
from covalent._results_manager import results_manager as rm
from covalent_dispatcher._db.dispatchdb import DispatchDB

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
    raise Exception(f"byebye {input}")


def test_dispatcher_functional():
    # Dispatch after starting the dispatcher server.

    dispatch_id = ct.dispatch(workflow)(name="q")
    output = ct.get_result(dispatch_id, wait=True).result

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


def test_results_dir_in_sublattice():
    # Test that a "non-standard" results_dir in a sublattice works.

    @ct.electron
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
    assert result_object.status == str(result_object.COMPLETED)

    assert output == 25

    rm._delete_result(
        dispatch_id=dispatch_id, results_dir="/tmp/results", remove_parent_directory=True
    )
