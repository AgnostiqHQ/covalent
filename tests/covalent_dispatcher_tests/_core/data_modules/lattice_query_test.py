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

"""
Tests for the querying lattices
"""


from unittest.mock import MagicMock

import pytest

from covalent_dispatcher._core.data_modules import lattice


@pytest.mark.asyncio
async def test_get(mocker):
    dispatch_id = "test_get"

    mock_retval = MagicMock()
    mock_result_obj = MagicMock()
    mock_result_obj.lattice.get_values = MagicMock(return_value=mock_retval)
    mocker.patch(
        "covalent_dispatcher._core.data_modules.lattice.get_result_object",
        return_value=mock_result_obj,
    )

    assert mock_retval == await lattice.get(dispatch_id, keys=["executor"])
