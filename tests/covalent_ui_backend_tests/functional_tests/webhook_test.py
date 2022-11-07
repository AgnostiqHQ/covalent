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

"""Result webhook functional test"""

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.config import get_config
from covalent._workflow.lattice import Lattice
from covalent_ui.result_webhook import get_ui_url, send_draw_request, send_update
from tests.covalent_ui_backend_tests.utils.assert_data.result_webhook import result_mock_data

mock_data = result_mock_data()
UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"


def get_mock_simple_workflow():
    """Construct a mock simple workflow corresponding to a lattice."""

    @ct.lattice(executor="local")
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


def test_get_ui_url():
    case1_test = mock_data["test_result_webhooks"]["case1"]
    ui_url = get_ui_url(case1_test["test_path"])
    if case1_test["response_data"]:
        assert ui_url == case1_test["response_data"]


@pytest.mark.asyncio
async def test_send_update():
    result_object = get_mock_result()
    response = await send_update(result_object)
    assert response is None


def test_send_draw_request():
    workflow = get_mock_simple_workflow()
    lattice = Lattice.deserialize_from_json(workflow.serialize_to_json())
    response = send_draw_request(lattice)
    assert response is None
