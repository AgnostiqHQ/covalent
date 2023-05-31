# Copyright 2023 Agnostiq Inc.
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

"""
Functions for serializing and deserializing assets
"""

from typing import Any

from ..._serialize.common import deserialize_asset, serialize_asset
from ..._serialize.electron import ASSET_TYPES


# Convenience functions for executor plugins
def serialize_node_asset(data: Any, key: str) -> bytes:
    return serialize_asset(data, ASSET_TYPES[key])


def deserialize_node_asset(data: bytes, key: str) -> Any:
    return deserialize_asset(data, ASSET_TYPES[key])
