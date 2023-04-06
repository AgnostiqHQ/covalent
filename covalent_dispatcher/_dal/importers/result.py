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

import os
from typing import Optional

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.lattice import (
    LATTICE_ERROR_FILENAME,
    LATTICE_INPUTS_FILENAME,
    LATTICE_RESULTS_FILENAME,
    LatticeSchema,
)
from covalent._shared_files.schemas.result import ResultAssets, ResultSchema
from covalent._shared_files.utils import format_server_url
from covalent_dispatcher._dal.asset import Asset, StorageType
from covalent_dispatcher._dal.electron import ElectronMeta
from covalent_dispatcher._dal.job import Job
from covalent_dispatcher._dal.result import Result, ResultMeta

from ..utils.uri_filters import AssetScope, URIFilterPolicy, filter_asset_uri
from .lattice import _get_lattice_meta, import_lattice_assets
from .tg import import_transport_graph

SERVER_URL = format_server_url(get_config("dispatcher.address"), get_config("dispatcher.port"))

URI_FILTER_POLICY = URIFilterPolicy[get_config("dispatcher.data_uri_filter_policy")]

app_log = logger.app_log


def import_result(
    res: ResultSchema,
    base_path: str,
    electron_id: Optional[int],
) -> ResultSchema:
    """Imports a ResultSchema into the DB"""

    dispatch_id = res.metadata.dispatch_id

    # If result already exists in the DB, it was previously registered
    # as a sublattice dispatch; in that case, just connect it to its
    # parent electron.
    with Result.session() as session:
        records = ResultMeta.get(
            session,
            fields={"id", "dispatch_id"},
            equality_filters={"dispatch_id": dispatch_id},
            membership_filters={},
        )
        if len(records) > 0:
            return _connect_result_to_electron(res, electron_id)

    # Main case: insert new lattice, electron, edge, and job records

    storage_path = os.path.join(base_path, dispatch_id)
    os.makedirs(storage_path)

    lattice_record_kwargs = _get_result_meta(res, storage_path, electron_id)
    lattice_record_kwargs.update(_get_lattice_meta(res.lattice, storage_path))

    with Result.session() as session:
        lattice_row = ResultMeta.insert(session, insert_kwargs=lattice_record_kwargs, flush=True)
        res_record = Result(session, lattice_row, True)
        res_assets = import_result_assets(session, res, res_record, storage_path)

        lat_assets = import_lattice_assets(
            session,
            res.lattice,
            res_record.lattice,
            storage_path,
        )

        tg = import_transport_graph(
            session,
            res.lattice.transport_graph,
            res_record.lattice,
            storage_path,
            electron_id,
        )

    lat = LatticeSchema(metadata=res.lattice.metadata, assets=lat_assets, transport_graph=tg)

    output = ResultSchema(metadata=res.metadata, assets=res_assets, lattice=lat)
    return _filter_remote_uris(output)


def _connect_result_to_electron(res: ResultSchema, parent_electron_id: int) -> ResultSchema:
    """Link a sublattice dispatch to its parent electron"""

    # Update the `electron_id` lattice field and propagate the
    # `Job.cancel_requested` to the sublattice dispatch's jobs.

    app_log.debug("connecting previously submitted subdispatch to parent electron")
    sub_result = Result.from_dispatch_id(res.metadata.dispatch_id, bare=True)
    with Result.session() as session:
        sub_result.set_value("electron_id", parent_electron_id, session)
        sub_result.set_value("root_dispatch_id", res.metadata.root_dispatch_id, session)

        parent_electron_record = ElectronMeta.get(
            session,
            fields={"id", "parent_lattice_id", "job_id"},
            equality_filters={"id": parent_electron_id},
            membership_filters={},
        )[0]
        parent_job_record = Job.get(
            session,
            fields={"id", "cancel_requested"},
            equality_filters={"id": parent_electron_record.job_id},
            membership_filters={},
        )[0]
        cancel_requested = parent_job_record.cancel_requested

        sub_electron_records = ElectronMeta.get(
            session,
            fields={"id", "parent_lattice_id", "job_id"},
            equality_filters={"parent_lattice_id": sub_result._lattice_id},
            membership_filters={},
        )

        job_ids = [rec.job_id for rec in sub_electron_records]

        Job.update_bulk(
            session,
            values={"cancel_requested": cancel_requested},
            equality_filters={},
            membership_filters={"id": job_ids},
        )

    return res


def _filter_remote_uris(manifest: ResultSchema) -> ResultSchema:
    dispatch_id = manifest.metadata.dispatch_id

    # Workflow-level
    for key, asset in manifest.assets:
        filtered_uri = filter_asset_uri(
            URI_FILTER_POLICY, asset.remote_uri, {}, AssetScope.DISPATCH, dispatch_id, None, key
        )
        asset.remote_uri = filtered_uri

    for key, asset in manifest.lattice.assets:
        filtered_uri = filter_asset_uri(
            URI_FILTER_POLICY, asset.remote_uri, {}, AssetScope.LATTICE, dispatch_id, None, key
        )
        asset.remote_uri = filtered_uri

    # Now filter each node
    tg = manifest.lattice.transport_graph
    for node in tg.nodes:
        for key, asset in node.assets:
            filtered_uri = filter_asset_uri(
                URI_FILTER_POLICY, asset.remote_uri, {}, AssetScope.NODE, dispatch_id, node.id, key
            )
            asset.remote_uri = filtered_uri

    return manifest


def _get_result_meta(res: ResultSchema, storage_path: str, electron_id: Optional[int]) -> dict:
    kwargs = {
        "dispatch_id": res.metadata.dispatch_id,
        "root_dispatch_id": res.metadata.root_dispatch_id,
        "status": res.metadata.status,
        "started_at": res.metadata.start_time,
        "completed_at": res.metadata.end_time,
    }
    db_kwargs = {
        "electron_id": electron_id,
    }
    kwargs.update(db_kwargs)

    return kwargs


def import_result_assets(
    session: Session,
    manifest: ResultSchema,
    record: Result,
    storage_path: str,
) -> ResultAssets:
    """Insert asset records and populate the asset link table"""
    asset_ids = {}

    for asset_key, asset, object_key in [
        ("inputs", manifest.assets.inputs, LATTICE_INPUTS_FILENAME),
        ("result", manifest.assets.result, LATTICE_RESULTS_FILENAME),
        ("error", manifest.assets.error, LATTICE_ERROR_FILENAME),
    ]:
        local_uri = os.path.join(storage_path, object_key)

        asset_kwargs = {
            "storage_type": StorageType.LOCAL.value,
            "storage_path": storage_path,
            "object_key": object_key,
            "digest_alg": "sha1",
            "digest_hex": asset.digest,
            "remote_uri": asset.uri,
        }
        asset_ids[asset_key] = Asset.insert(session, insert_kwargs=asset_kwargs, flush=False)

        # Send this back to the client
        asset.digest = None
        asset.remote_uri = f"file://{local_uri}"

    session.flush()

    for key, asset_rec in asset_ids.items():
        record.associate_asset(session, key, asset_rec.id)

    return manifest.assets
