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

"""Unit tests for lattice"""

from dataclasses import asdict

import pytest

import covalent as ct
from covalent._shared_files.defaults import DefaultMetadataValues, postprocess_prefix

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())


def test_lattice_draw(mocker):
    mock_send_draw_req = mocker.patch("covalent_ui.result_webhook.send_draw_request")

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.draw(2)

    mock_send_draw_req.assert_called_once()


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
