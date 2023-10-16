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

"""Unit tests for lattice"""

from dataclasses import asdict

import pytest

import covalent as ct
from covalent._shared_files.defaults import DefaultMetadataValues, postprocess_prefix
from covalent._shared_files.utils import get_ui_url

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())


def test_lattice_draw(mocker, capsys):
    draw_preview_url = get_ui_url("/preview")
    mock_send_draw_req = mocker.patch("covalent_ui.result_webhook.send_draw_request")
    mock_webbrowser_open = mocker.patch("webbrowser.open")

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.draw(2)

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"To preview the transport graph of the lattice, visit {draw_preview_url}\n"
    )

    mock_send_draw_req.assert_called_once()
    mock_webbrowser_open.assert_called_once()


def test_lattice_workflow_executor_settings():
    """Check that workflow executor is set from defaults if not set explicitly"""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    @ct.lattice(workflow_executor="custom_postprocessor")
    def workflow_2(x):
        return task(x)

    assert not workflow.metadata["workflow_executor"]
    workflow.build_graph(1)
    assert workflow.metadata["workflow_executor"] == DEFAULT_METADATA_VALUES["workflow_executor"]
    workflow_2.build_graph(1)
    assert workflow_2.metadata["workflow_executor"] == "custom_postprocessor"


def test_lattice_executor_settings():
    """Check that executor is set from defaults if not set explicitly"""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    @ct.lattice(executor="custom_executor")
    def workflow_2(x):
        return task(x)

    assert not workflow.metadata["executor"]
    workflow.build_graph(1)
    assert workflow.metadata["executor"] == DEFAULT_METADATA_VALUES["executor"]
    workflow_2.build_graph(1)
    assert workflow_2.metadata["executor"] == "custom_executor"


def test_lattice_build_graph(mocker):
    """Test the build graph method in lattice."""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    original_exhaustive_value = ct._shared_files.config.get_config("sdk.exhaustive_postprocess")
    ct._shared_files.config.set_config("sdk.exhaustive_postprocess", "false")
    workflow.build_graph(1)
    assert workflow.transport_graph.get_node_value(2, "name") == f"{postprocess_prefix}reconstruct"
    ct._shared_files.config.set_config("sdk.exhaustive_postprocess", "true")
    workflow.build_graph(1)
    assert workflow.transport_graph.get_node_value(2, "name") == postprocess_prefix
    ct._shared_files.config.set_config("sdk.exhaustive_postprocess", original_exhaustive_value)


def test_lattice_build_graph_with_extra_args(mocker):
    """Test the build graph method in lattice with extra args / kwargs."""

    @ct.electron
    def task(x, y):
        return x + y

    @ct.lattice
    def workflow(x, y):
        return task(x, y)

    with pytest.raises(
        ValueError, match="Too many positional arguments given, expected 2, received 3"
    ):
        workflow.build_graph(1, 2, 3)

    with pytest.raises(
        ValueError, match="Too many positional arguments given, expected 0, received 1"
    ):
        workflow.build_graph(1, x=2)

    # no issues here
    workflow.build_graph(1, y=2)

    with pytest.raises(ValueError, match="Unexpected keyword arguments: a, b"):
        workflow.build_graph(1, a=2, b=3)

    with pytest.raises(ValueError, match="Unexpected keyword arguments: a"):
        workflow.build_graph(a=1)

    # fewer arguments handled internally by function call
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'y'"):
        workflow.build_graph(1)


def test_replace_electrons_property():
    @ct.electron
    def task(x):
        return x**2

    @ct.electron
    def replacement_task(x):
        return x**3

    @ct.lattice
    def workflow(x):
        return task(x)

    assert workflow.replace_electrons == {}

    workflow._replace_electrons = {"task": replacement_task}
    assert workflow.replace_electrons["task"](3) == 27
    del workflow.__dict__["_replace_electrons"]
