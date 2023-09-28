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

"""Settings request and response model"""

import enum
from typing import Union

from pydantic import BaseModel


class GetSettingsResponseModel(BaseModel):
    """Get Settings response model"""

    client: Union[dict, None] = None
    server: Union[dict, None] = None


class UpdateSettingsResponseModel(BaseModel):
    """Update Settings response model"""

    data: str


class Validators(enum.Enum):
    """Validate settings overwrite"""

    DISPATCHER = "dispatcher"
    DASK = "dask"
    WORKFLOW_DATA = "workflow_data"
    USER_INTERFACE = "user_interface"
