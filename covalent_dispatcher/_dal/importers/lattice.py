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


"""Functions to transform ResultSchema -> Result"""

import json
import os

from sqlalchemy.orm import Session

from covalent._shared_files.schemas.lattice import (
    LATTICE_CALL_AFTER_FILENAME,
    LATTICE_CALL_BEFORE_FILENAME,
    LATTICE_COVA_IMPORTS_FILENAME,
    LATTICE_DEPS_FILENAME,
    LATTICE_DOCSTRING_FILENAME,
    LATTICE_ERROR_FILENAME,
    LATTICE_FUNCTION_FILENAME,
    LATTICE_FUNCTION_STRING_FILENAME,
    LATTICE_INPUTS_FILENAME,
    LATTICE_LATTICE_IMPORTS_FILENAME,
    LATTICE_NAMED_ARGS_FILENAME,
    LATTICE_NAMED_KWARGS_FILENAME,
    LATTICE_RESULTS_FILENAME,
    LATTICE_STORAGE_TYPE,
    LatticeAssets,
    LatticeSchema,
)
from covalent_dispatcher._dal.asset import Asset, StorageType
from covalent_dispatcher._dal.lattice import Lattice


def _get_lattice_meta(lat: LatticeSchema, storage_path) -> dict:
    kwargs = {
        "storage_path": storage_path,
        "storage_type": LATTICE_STORAGE_TYPE,
        "name": lat.metadata.name,
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
        "named_args_filename": LATTICE_NAMED_ARGS_FILENAME,
        "named_kwargs_filename": LATTICE_NAMED_KWARGS_FILENAME,
        "results_filename": LATTICE_RESULTS_FILENAME,
        "deps_filename": LATTICE_DEPS_FILENAME,
        "call_before_filename": LATTICE_CALL_BEFORE_FILENAME,
        "call_after_filename": LATTICE_CALL_AFTER_FILENAME,
        "cova_imports_filename": LATTICE_COVA_IMPORTS_FILENAME,
        "lattice_imports_filename": LATTICE_LATTICE_IMPORTS_FILENAME,
    }
    kwargs.update(legacy_kwargs)
    return kwargs


def import_lattice_assets(
    session: Session,
    lat: LatticeSchema,
    record: Lattice,
    storage_path: str,
) -> LatticeAssets:
    """Insert asset records and populate the asset link table"""
    asset_ids = {}

    for asset_key, asset, object_key in [
        ("workflow_function", lat.assets.workflow_function, LATTICE_FUNCTION_FILENAME),
        (
            "workflow_function_string",
            lat.assets.workflow_function_string,
            LATTICE_FUNCTION_STRING_FILENAME,
        ),
        ("__doc__", lat.assets.doc, LATTICE_DOCSTRING_FILENAME),
        ("named_args", lat.assets.named_args, LATTICE_NAMED_ARGS_FILENAME),
        ("named_kwargs", lat.assets.named_kwargs, LATTICE_NAMED_KWARGS_FILENAME),
        ("cova_imports", lat.assets.cova_imports, LATTICE_COVA_IMPORTS_FILENAME),
        ("lattice_imports", lat.assets.lattice_imports, LATTICE_LATTICE_IMPORTS_FILENAME),
        ("deps", lat.assets.deps, LATTICE_DEPS_FILENAME),
        ("call_before", lat.assets.call_before, LATTICE_CALL_BEFORE_FILENAME),
        ("call_after", lat.assets.call_after, LATTICE_CALL_AFTER_FILENAME),
    ]:
        local_uri = os.path.join(storage_path, object_key)

        asset_kwargs = {
            "storage_type": StorageType.LOCAL.value,
            "storage_path": storage_path,
            "object_key": object_key,
            "digest_alg": asset.digest_alg,
            "digest": asset.digest,
            "remote_uri": asset.uri,
            "size": asset.size,
        }
        asset_ids[asset_key] = Asset.insert(session, insert_kwargs=asset_kwargs, flush=False)

        # Send this back to the client
        asset.digest = None
        asset.remote_uri = f"file://{local_uri}"

    session.flush()

    for key, asset_rec in asset_ids.items():
        record.associate_asset(session, key, asset_rec.id)

    return lat.assets
