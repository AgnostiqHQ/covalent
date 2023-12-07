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
