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
import os

from sqlalchemy.orm import Session

from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.lattice import (
    LATTICE_DOCSTRING_FILENAME,
    LATTICE_ERROR_FILENAME,
    LATTICE_FUNCTION_FILENAME,
    LATTICE_FUNCTION_STRING_FILENAME,
    LATTICE_HOOKS_FILENAME,
    LATTICE_INPUTS_FILENAME,
    LATTICE_RESULTS_FILENAME,
    LATTICE_STORAGE_TYPE,
    LatticeAssets,
    LatticeSchema,
)
from covalent_dispatcher._dal.asset import Asset
from covalent_dispatcher._dal.lattice import Lattice
from covalent_dispatcher._object_store.base import BaseProvider, TransferDirection


def _get_lattice_meta(lat: LatticeSchema, storage_path) -> dict:
    results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir")
    kwargs = {
        "results_dir": results_dir,  # Needed for current executors
        "storage_path": storage_path,
        "storage_type": LATTICE_STORAGE_TYPE,
        "name": lat.metadata.name,
        "python_version": lat.metadata.python_version,
        "covalent_version": lat.metadata.covalent_version,
        "executor": lat.metadata.executor,
        "executor_data": json.dumps(lat.metadata.executor_data),
        "workflow_executor": lat.metadata.workflow_executor,
        "workflow_executor_data": json.dumps(lat.metadata.workflow_executor_data),
    }
    num_nodes = len(lat.transport_graph.nodes)
    db_kwargs = {
        "electron_num": num_nodes,
        "completed_electron_num": 0,
    }
    kwargs.update(db_kwargs)

    legacy_kwargs = {
        "docstring_filename": LATTICE_DOCSTRING_FILENAME,
        "function_filename": LATTICE_FUNCTION_FILENAME,
        "function_string_filename": LATTICE_FUNCTION_STRING_FILENAME,
        "error_filename": LATTICE_ERROR_FILENAME,
        "inputs_filename": LATTICE_INPUTS_FILENAME,
        "results_filename": LATTICE_RESULTS_FILENAME,
        "hooks_filename": LATTICE_HOOKS_FILENAME,
    }
    kwargs.update(legacy_kwargs)
    return kwargs


def import_lattice_assets(
    session: Session,
    dispatch_id: str,
    lat: LatticeSchema,
    record: Lattice,
    object_store: BaseProvider,
) -> LatticeAssets:
    """Insert asset records and populate the asset link table"""
    asset_ids = {}

    # Register built-in assets
    for asset_key, asset in lat.assets:
        # Deal with these later
        if asset_key == "_custom":
            continue

        storage_path, object_key = object_store.get_uri_components(
            dispatch_id=dispatch_id,
            node_id=None,
            asset_key=asset_key,
        )

        local_uri = os.path.join(storage_path, object_key)
        asset_kwargs = {
            "storage_type": object_store.scheme,
            "storage_path": storage_path,
            "object_key": object_key,
            "digest_alg": asset.digest_alg,
            "digest": asset.digest,
            "remote_uri": asset.uri,
            "size": asset.size,
        }
        asset_ids[asset_key] = Asset.create(session, insert_kwargs=asset_kwargs, flush=False)

        # Send this back to the client
        asset.digest = None
        remote_uri = object_store.get_public_uri(
            storage_path,
            object_key,
            transfer_direction=TransferDirection.upload,
        )
        asset.remote_uri = remote_uri

    # Write asset records to DB
    session.flush()

    lattice_asset_links = [
        record.associate_asset(session, key, asset_rec.id) for key, asset_rec in asset_ids.items()
    ]
    session.flush()

    return lat.assets
