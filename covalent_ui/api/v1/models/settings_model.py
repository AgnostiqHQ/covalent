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
