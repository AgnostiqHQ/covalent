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

from os.path import abspath, dirname

from pytest_mock import mocker

import tests.covalent_ui_backend_tests.utils.main as main
from tests.covalent_ui_backend_tests.utils.assert_data.service_app import seed_service_app_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/assert_data/summary_data.json"
# with open(output_path, "r") as output_json:
#     output_data = json.load(output_json)
output_data = seed_service_app_data()


def test_ui_service_result(mocker):
    """Test overview"""
    import os

    dbpath = os.path.join("tests/covalent_ui_backend_tests/utils/data", "mock_db.sqlite")

    def __init__(self, dbpath=dbpath):
        self._dbpath = dbpath

    from covalent_dispatcher._db.dispatchdb import DispatchDB

    mocker.patch.object(DispatchDB, "__init__", __init__)
    test_data = output_data["test_result"]["case1"]
    response = object_test_template(
        api_path=output_data["test_result"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_ui_service_db_path(mocker):
    dbpath = "/Users/root/covalent/results.db"

    def __init__(self, dbpath=dbpath):
        self._dbpath = dbpath

    from covalent_dispatcher._db.dispatchdb import DispatchDB

    mocker.patch.object(DispatchDB, "__init__", __init__)
    response = object_test_template(
        api_path="/api/db-path",
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    result = response.json().replace("\\", "").replace('"', "")
    assert result == dbpath
