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


"""Functions to transform Lattice -> LatticeSchema"""


from covalent._shared_files.schemas.asset import AssetSchema
from covalent._shared_files.schemas.lattice import LatticeAssets, LatticeMetadata, LatticeSchema
from covalent_dispatcher._dal.lattice import ASSET_KEYS, METADATA_KEYS, Lattice

from .tg import export_transport_graph


def _export_lattice_meta(lat: Lattice) -> LatticeMetadata:
    metadata_kwargs = {key: lat.get_value(key, None, refresh=False) for key in METADATA_KEYS}
    return LatticeMetadata(**metadata_kwargs)


def _export_lattice_assets(lat: Lattice) -> LatticeAssets:
    manifests = {}
    for asset_key in ASSET_KEYS:
        asset = lat.assets[asset_key]
        size = asset.size
        digest_alg = asset.digest_alg
        digest = asset.digest
        scheme = asset.storage_type.value
        remote_uri = f"{scheme}://{asset.storage_path}/{asset.object_key}"
        manifests[asset_key] = AssetSchema(
            remote_uri=remote_uri, size=size, digest_alg=digest_alg, digest=digest
        )
    return LatticeAssets(**manifests)


def export_lattice(lat: Lattice) -> LatticeSchema:
    metadata = _export_lattice_meta(lat)
    assets = _export_lattice_assets(lat)
    transport_graph = export_transport_graph(lat.transport_graph)
    return LatticeSchema(metadata=metadata, assets=assets, transport_graph=transport_graph)
