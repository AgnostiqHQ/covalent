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

"""Unit tests for results manager."""

import os
from contextlib import nullcontext
from unittest.mock import call

import pytest
import requests

from covalent._results_manager.results_manager import (
    _get_result_from_file,
    cancel,
    get_result,
    sync,
)


@pytest.mark.parametrize("wait", [True, False])
def test_get_result(mocker, wait):
    def open_result(dispatch_id, results_dir, wait):
        if not wait:
            filename = os.path.join(results_dir, "result.pkl")
            # Should raise FileNotFoundError
            open(filename)
            assert False

    result_from_file_mock = mocker.patch(
        "covalent._results_manager.results_manager._get_result_from_file", side_effect=open_result
    )

    context = pytest.raises(FileNotFoundError) if not wait else nullcontext()

    with context:
        get_result("sample-dispatch-id", "sample_results_dir", wait=wait)

    if not wait:
        return

    result_from_file_mock.assert_called_once_with("sample-dispatch-id", "sample_results_dir", True)


def test_get_result_from_file(mocker):
    pass


def test_delete_result(mocker):
    pass


def test_redispatch_result(mocker):
    pass


@pytest.mark.parametrize(
    "dispatch_id", ["sample-dispatch-id", ["sample-dispatch-1", "sample-dispatch-2"], None]
)
def test_sync(mocker, dispatch_id):
    result_from_file_mock = mocker.patch(
        "covalent._results_manager.results_manager._get_result_from_file", return_value=None
    )
    glob_mock = mocker.patch(
        "glob.glob",
        return_value=[
            "sample_results_dir/sample-dispatch-1",
            "sample_results_dir/sample-dispatch-2",
        ],
    )

    sync(dispatch_id, "sample_results_dir")

    if dispatch_id:
        if isinstance(dispatch_id, str):
            result_from_file_mock.assert_called_once_with(dispatch_id, "sample_results_dir", True)
        elif isinstance(dispatch_id, list):
            result_from_file_mock.assert_has_calls(
                [call(_id, "sample_results_dir", True) for _id in dispatch_id]
            )
    else:
        glob_mock.assert_called_once_with("sample_results_dir/*/")
        result_from_file_mock.assert_has_calls(
            [
                call("sample-dispatch-1", "sample_results_dir", True),
                call("sample-dispatch-2", "sample_results_dir", True),
            ]
        )


def test_cancel(mocker):
    response = requests.Response()
    response.status_code = 200
    response._content = "ok".encode("utf-8")
    post_mock = mocker.patch("requests.post", return_value=response)

    r = cancel("sample-dispatch-id", "dispatcher:8000")

    post_mock.assert_called_once_with(
        "http://dispatcher:8000/api/cancel", data="sample-dispatch-id".encode("utf-8")
    )

    assert r == "ok"
