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

from covalent._shared_files.utils import filter_null_metadata


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
