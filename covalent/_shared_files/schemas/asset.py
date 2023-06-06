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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from typing import Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class AssetSchema(BaseModel):
    digest_alg: Optional[str]
    digest: Optional[str]
    uri: Optional[str]
    remote_uri: Optional[str]

    # Size of the asset in bytes
    size: Optional[int] = 0


@dataclass
class AssetUpdate:
    remote_uri: Optional[str] = None
    size: Optional[int] = None
    digest_alg: Optional[str] = None
    digest: Optional[str] = None
