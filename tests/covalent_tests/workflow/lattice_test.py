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

"""Unit tests for electron"""

from pathlib import Path
from uuid import UUID

import numpy

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.depsbash import DepsBash
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject

TEST_RESULTS_DIR = "/tmp/results"


def get_mock_simple_workflow():
    """Construct a mock simple workflow corresponding to a lattice."""

    @ct.lattice(executor="le")
    def workflow(x):
        return x

    return workflow


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    workflow = get_mock_simple_workflow()

    workflow.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(
        received_workflow, workflow.metadata["results_dir"], "pipeline_workflow"
    )

    return result_object


def test_lattice_draw(mocker):
    """Test draw functionality of Lattice"""
    mock_send_draw_req = mocker.patch("covalent_ui.result_webhook.send_draw_request")

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.draw(2)

    mock_send_draw_req.assert_called_once()


def test_serialize_to_json():
    """Lattice object fixture."""

    workflow = get_mock_simple_workflow()

    workflow.build_graph(5)
    workflow.cova_imports = set({"dummy_module"})
    workflow.electron_outputs = {
        "0": TransportableObject(4),
        "2": TransportableObject(12),
        "4": TransportableObject(125),
        "6": TransportableObject(1500),
    }

    json_workflow = workflow.serialize_to_json()

    new_workflow = Lattice.deserialize_from_json(json_workflow)
    assert json_workflow == new_workflow.serialize_to_json()


def test_call():
    """Test __call__ functionality of Lattice"""
    result = get_mock_result()
    res = result.lattice.__call__({"executor": "docker"})
    assert res == {"executor": "docker"}


def test_lattice_wrapper():
    """Test lattice wrapper functionality"""

    def call_before_lattice():
        with open("/tmp/test.txt", "w"):
            pass

    def call_after_lattice():
        Path("/tmp/test.txt").unlink()

    @ct.lattice(
        backend="local",
        call_before=ct.DepsCall(call_before_lattice),
        deps_bash=DepsBash(["echo 'Hello World' >> /tmp/path.txt"]),
        call_after=ct.DepsCall(call_after_lattice),
    )
    def read_file():
        with open("/tmp/path.txt", "r") as f:
            return f.read()

    result_dispatch_1 = ct.dispatch(read_file)()
    r = ct.get_result(result_dispatch_1, wait=True)
    print(r.result)

    res2 = ct.lattice(deps_bash=DepsBash(["echo $PATH"]))

    assert 1 == 1


def test_lattice_metadata():
    """Test get metadata functionality of Lattice"""
    result = get_mock_result()
    result.lattice.set_metadata("executor", "docker")
    metadata = result.lattice.get_metadata("executor")
    assert metadata == "docker"


def test_lattice_dispatch():
    """Test dispatch functionality of Lattice"""
    result = get_mock_result()
    res = result.lattice.dispatch("pipeline")
    assert isinstance(UUID(res), UUID)


def test_lattice_dispatch_sync():
    """Test dispatch_sync functionality of Lattice"""
    result = get_mock_result()
    res = result.lattice.dispatch_sync("pipeline2")
    assert isinstance(res, Result)


def test_lattice_deps():
    """Construct a mock workflow corresponding to a lattice for testing deps_pip"""
    numpy_pkg = ct.DepsPip(packages=["numpy==1.22.4"])

    @ct.lattice(deps_pip=numpy_pkg)
    def workflow():
        matrix = numpy.identity(3)
        return numpy.sum(matrix)

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    assert res.result == 3.0


def test_lattice_multi_deps():
    """Construct a mock workflow corresponding to a lattice for testing deps_pip"""
    numpy_pkg = ["numpy"]

    @ct.lattice(deps_pip=numpy_pkg)
    def workflow():
        matrix = numpy.identity(3)
        return numpy.sum(matrix)

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    assert res.result == 3.0
