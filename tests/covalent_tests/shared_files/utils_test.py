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


"""Unit tests for Covalent shared util functions."""

import pytest

from covalent._shared_files.config import get_config
from covalent._shared_files.utils import filter_null_metadata, format_server_url, get_named_params


@pytest.mark.parametrize(
    "meta_dict,expected",
    [
        ({}, {}),
        ({"a": 1}, {"a": 1}),
        ({"a": 1, "b": None}, {"a": 1}),
    ],
)
def test_filter_null_metadata(meta_dict, expected):
    """Test the filter null metadata function."""
    filtered = filter_null_metadata(meta_dict)
    assert filtered == expected


def test_get_named_params():
    """Tests the changes I made in covalent/covalent/_shared_files/utils.py for fixing ValueError in when using KEYWORD_ONLU parameter in electron func"""

    def test_func(a, *, b):
        return a + b

    named_args, named_kwargs = get_named_params(test_func, [1], {"b": 2})

    assert named_args == {"a": 1}
    assert named_kwargs == {"b": 2}


def test_format_server_url():
    """Test the convenience function to format server urls."""

    base_url = format_server_url()

    addr = get_config("dispatcher.address")
    port = int(get_config("dispatcher.port"))

    assert base_url == f"http://{addr}:{port}"
