# Copyright 2023 Agnostiq Inc.
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


"""Unit tests for the API client"""

import json
from unittest.mock import MagicMock

import pytest

from covalent._api.apiclient import CovalentAPIClient


@pytest.fixture
def mock_session():
    sess = MagicMock()


def test_header_injection(mocker):
    extra_headers = {"x-custom-header": "value"}
    headers = {"Content-Length": "128"}
    expected_headers = headers.copy()
    expected_headers.update(extra_headers)
    mock_session = MagicMock()
    environ = {"COVALENT_EXTRA_HEADERS": json.dumps(extra_headers)}
    mocker.patch("os.environ", environ)
    mocker.patch("requests.Session.__enter__", return_value=mock_session)

    CovalentAPIClient("http://localhost").post("/docs", headers=headers)
    mock_session.post.assert_called_with("http://localhost/docs", headers=expected_headers)
