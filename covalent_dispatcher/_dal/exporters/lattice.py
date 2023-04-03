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


"""Functions to transform Lattice -> LatticeSchema"""


from covalent._shared_files.schemas.asset import AssetSchema
from covalent._shared_files.schemas.lattice import LatticeAssets, LatticeMetadata, LatticeSchema
from covalent_dispatcher._dal.lattice import ASSET_KEYS, METADATA_KEYS, Lattice

from .tg import export_transport_graph

KEY_SUBSTITUTIONS = {"__name__": "name", "__doc__": "doc"}


def _export_lattice_meta(lat: Lattice) -> LatticeMetadata:
    metadata_kwargs = {}
    for key in METADATA_KEYS:
        param = KEY_SUBSTITUTIONS.get(key, key)
        metadata_kwargs[param] = lat.get_value(key, None, refresh=False)

    return LatticeMetadata(**metadata_kwargs)


def _export_lattice_assets(lat: Lattice, data_uri_prefix: str) -> LatticeAssets:
    manifests = {}
    for asset_key in ASSET_KEYS:
        param = KEY_SUBSTITUTIONS.get(asset_key, asset_key)
        asset = lat.assets[asset_key]
        scheme = asset.storage_type.value
        remote_uri = f"{scheme}://{asset.storage_path}/{asset.object_key}"
        manifests[param] = AssetSchema(remote_uri=remote_uri)
    return LatticeAssets(**manifests)


def export_lattice(lat: Lattice, data_uri_prefix: str, node_data_uri_prefix: str) -> LatticeSchema:
    metadata = _export_lattice_meta(lat)
    assets = _export_lattice_assets(lat, data_uri_prefix)
    transport_graph = export_transport_graph(lat.transport_graph, node_data_uri_prefix)
    return LatticeSchema(metadata=metadata, assets=assets, transport_graph=transport_graph)
