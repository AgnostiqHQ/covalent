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


"""Functions to transform ResultSchema -> Result"""

import json
from typing import Dict, Tuple

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.schemas.electron import (
    ELECTRON_ERROR_FILENAME,
    ELECTRON_FUNCTION_FILENAME,
    ELECTRON_FUNCTION_STRING_FILENAME,
    ELECTRON_HOOKS_FILENAME,
    ELECTRON_RESULTS_FILENAME,
    ELECTRON_STDERR_FILENAME,
    ELECTRON_STDOUT_FILENAME,
    ELECTRON_STORAGE_TYPE,
    ELECTRON_VALUE_FILENAME,
    ElectronAssets,
    ElectronSchema,
)
from covalent_dispatcher._dal.asset import Asset
from covalent_dispatcher._dal.electron import ElectronMeta
from covalent_dispatcher._dal.lattice import Lattice
from covalent_dispatcher._db import models
from covalent_dispatcher._db.write_result_to_db import get_electron_type
from covalent_dispatcher._object_store.base import BaseProvider, TransferDirection

app_log = logger.app_log


def import_electron(
    session: Session,
    dispatch_id: str,
    e: ElectronSchema,
    lat: Lattice,
    object_store: BaseProvider,
    job_id: int,
) -> Tuple[models.Electron, ElectronSchema]:
    """Returns (electron_id, ElectronSchema)"""

    electron_assets, asset_recs = import_electron_assets(
        session,
        dispatch_id,
        e,
        object_store,
    )

    # Hack for legacy DB columns
    node_storage_path = asset_recs["function"].storage_path

    electron_kwargs = _get_electron_meta(e, lat, node_storage_path, job_id)
    electron_row = ElectronMeta.create(session, insert_kwargs=electron_kwargs, flush=False)

    return (
        electron_row,
        asset_recs,
        ElectronSchema(id=e.id, metadata=e.metadata, assets=electron_assets),
    )


def _get_electron_meta(
    e: ElectronSchema, lat: Lattice, node_storage_path: str, job_id: int
) -> dict:
    kwargs = {
        "transport_graph_node_id": e.id,
        "task_group_id": e.metadata.task_group_id,
        "name": e.metadata.name,
        "executor": e.metadata.executor,
        "executor_data": json.dumps(e.metadata.executor_data),
        "status": e.metadata.status,
        "started_at": e.metadata.start_time,
        "completed_at": e.metadata.end_time,
    }
    db_kwargs = {
        "parent_lattice_id": lat.metadata.primary_key,
        "type": get_electron_type(e.metadata.name),
        "job_id": job_id,
    }
    kwargs.update(db_kwargs)

    legacy_kwargs = {
        "storage_type": ELECTRON_STORAGE_TYPE,
        "storage_path": node_storage_path,
        "function_filename": ELECTRON_FUNCTION_FILENAME,
        "function_string_filename": ELECTRON_FUNCTION_STRING_FILENAME,
        "results_filename": ELECTRON_RESULTS_FILENAME,
        "value_filename": ELECTRON_VALUE_FILENAME,
        "stdout_filename": ELECTRON_STDOUT_FILENAME,
        "stderr_filename": ELECTRON_STDERR_FILENAME,
        "error_filename": ELECTRON_ERROR_FILENAME,
        "hooks_filename": ELECTRON_HOOKS_FILENAME,
    }
    kwargs.update(legacy_kwargs)
    return kwargs


def import_electron_assets(
    session: Session,
    dispatch_id,
    e: ElectronSchema,
    object_store: BaseProvider,
) -> Tuple[ElectronAssets, Dict[str, models.Asset]]:
    """Insert asset records


    Returns pair (ElectronAssets, asset_records), where
    `asset_records` is a mapping from asset key to asset records.

    """

    # Maps asset keys to asset records
    asset_recs = {}

    for asset_key, asset in e.assets:
        # Register these later
        if asset_key == "_custom":
            continue

        node_storage_path, object_key = object_store.get_uri_components(
            dispatch_id,
            e.id,
            asset_key,
        )

        asset_kwargs = {
            "storage_type": object_store.scheme,
            "storage_path": node_storage_path,
            "object_key": object_key,
            "digest_alg": asset.digest_alg,
            "digest": asset.digest,
            "remote_uri": asset.uri,
            "size": asset.size,
        }
        asset_recs[asset_key] = Asset.create(session, insert_kwargs=asset_kwargs, flush=False)

        # Send this back to the client
        remote_uri = object_store.get_public_uri(
            node_storage_path,
            object_key,
            transfer_direction=TransferDirection.upload,
        )
        asset.digest = None
        asset.remote_uri = remote_uri

    # Declare an asset for sublattice manifests
    electron_type = get_electron_type(e.metadata.name)
    if electron_type == "sublattice":
        object_key = "result.tobj"
        asset_kwargs = {
            "storage_type": object_store.scheme,
            "storage_path": node_storage_path,
            "object_key": object_key,
            "digest_alg": None,
            "digest": None,
            "remote_uri": None,
            "size": 0,
        }
        asset_recs["sublattice_manifest"] = Asset.create(
            session, insert_kwargs=asset_kwargs, flush=False
        )

    return e.assets, asset_recs
