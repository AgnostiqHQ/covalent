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


"""Functions to transform Electron -> ElectronSchema"""


from covalent._shared_files import logger
from covalent._shared_files.schemas.asset import AssetSchema
from covalent._shared_files.schemas.electron import (
    ElectronAssets,
    ElectronMetadata,
    ElectronSchema,
)
from covalent_dispatcher._dal.electron import ASSET_KEYS, Electron

app_log = logger.app_log


# Electrons are assumed to represent full DB records
def _export_electron_meta(e: Electron) -> ElectronMetadata:
    task_group_id = e.get_value("task_group_id", None, refresh=False)
    name = e.get_value("name", None, refresh=False)
    executor = e.get_value("executor", None, refresh=False)
    executor_data = e.get_value("executor_data", None, refresh=False)
    qelectron_data_exists = e.get_value("qelectron_data_exists", None, refresh=False)
    sub_dispatch_id = e.get_value("sub_dispatch_id", None, refresh=False)
    status = e.get_value("status", None, refresh=False)
    start_time = e.get_value("start_time", None, refresh=False)
    end_time = e.get_value("end_time", None, refresh=False)

    return ElectronMetadata(
        task_group_id=task_group_id,
        name=name,
        executor=executor,
        executor_data=executor_data,
        qelectron_data_exists=qelectron_data_exists,
        sub_dispatch_id=sub_dispatch_id,
        status=str(status),
        start_time=start_time,
        end_time=end_time,
    )


def _export_electron_assets(e: Electron) -> ElectronAssets:
    manifests = {}
    for asset_key in ASSET_KEYS:
        asset = e.assets[asset_key]
        size = asset.size
        digest_alg = asset.digest_alg
        digest = asset.digest
        scheme = asset.storage_type.value
        remote_uri = f"{scheme}://{asset.storage_path}/{asset.object_key}"
        manifests[asset_key] = AssetSchema(
            remote_uri=remote_uri, size=size, digest_alg=digest_alg, digest=digest
        )

    return ElectronAssets(**manifests)


def export_electron(e: Electron) -> ElectronSchema:
    metadata = _export_electron_meta(e)
    assets = _export_electron_assets(e)
    return ElectronSchema(id=e.node_id, metadata=metadata, assets=assets)
