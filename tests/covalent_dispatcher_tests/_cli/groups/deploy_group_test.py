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

from unittest.mock import patch

import pytest

from covalent_dispatcher._cli.groups.deploy_group import validate_args, validate_region


def test_validate_region(mocker):
    """Test validate region"""
    region_name = "us-east-1"
    with patch("covalent_dispatcher._cli.groups.deploy_group.boto3.client") as mock_boto3_client:
        mock_client = mock_boto3_client.return_value
        mock_client.describe_regions.return_value = {"Regions": [{"RegionName": region_name}]}

        result = validate_region(region_name)

        assert result is True


@pytest.mark.parametrize(
    "args",
    [{"region": "test pytest"}],
)
def test_validate_args(mocker, args):
    """Test validate args"""
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group.validate_region",
        return_value=False,
    )
    result = validate_args(args)
    assert result == f"Unable to find the provided region: {args['region']}"
