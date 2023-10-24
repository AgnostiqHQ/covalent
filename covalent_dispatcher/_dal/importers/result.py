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

import os
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.lattice import LatticeSchema
from covalent._shared_files.schemas.result import ResultAssets, ResultSchema
from covalent._shared_files.utils import format_server_url
from covalent_dispatcher._dal.asset import Asset
from covalent_dispatcher._dal.electron import ElectronMeta
from covalent_dispatcher._dal.job import Job
from covalent_dispatcher._dal.result import Result, ResultMeta
from covalent_dispatcher._object_store.local import BaseProvider, local_store

from ..asset import copy_asset_meta
from ..tg_ops import TransportGraphOps
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
            return _connect_result_to_electron(session, res, electron_id)

    # Main case: insert new lattice, electron, edge, and job records

    storage_path = os.path.join(base_path, dispatch_id)
    os.makedirs(storage_path)

    lattice_record_kwargs = _get_result_meta(res, storage_path, electron_id)
    lattice_record_kwargs.update(_get_lattice_meta(res.lattice, storage_path))

    with Result.session() as session:
        st = datetime.now()
        lattice_row = ResultMeta.create(session, insert_kwargs=lattice_record_kwargs, flush=True)
        res_record = Result(session, lattice_row, True)
        res_assets = import_result_assets(session, res, res_record, local_store)

        lat_assets = import_lattice_assets(
            session,
            dispatch_id,
            res.lattice,
            res_record.lattice,
            local_store,
        )
        et = datetime.now()
        delta = (et - st).total_seconds()
        app_log.debug(f"{dispatch_id}: Inserting lattice took {delta} seconds")

        st = datetime.now()
        tg = import_transport_graph(
            session,
            dispatch_id,
            res.lattice.transport_graph,
            res_record.lattice,
            local_store,
            electron_id,
        )
        et = datetime.now()
        delta = (et - st).total_seconds()
        app_log.debug(f"{dispatch_id}: Inserting transport graph took {delta} seconds")

    lat = LatticeSchema(metadata=res.lattice.metadata, assets=lat_assets, transport_graph=tg)

    output = ResultSchema(metadata=res.metadata, assets=res_assets, lattice=lat)
    st = datetime.now()
    filtered_uris = _filter_remote_uris(output)
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"{dispatch_id}: Filtering URIs took {delta} seconds")
    return filtered_uris


def _connect_result_to_electron(
    session: Session, res: ResultSchema, parent_electron_id: int
) -> ResultSchema:
    """Link a sublattice dispatch to its parent electron"""

    # Update the `electron_id` lattice field and propagate the
    # `Job.cancel_requested` to the sublattice dispatch's jobs.

    app_log.debug("connecting previously submitted subdispatch to parent electron")
    sub_result = Result.from_dispatch_id(res.metadata.dispatch_id, bare=True)

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
        if asset.remote_uri:
            filtered_uri = filter_asset_uri(
                URI_FILTER_POLICY,
                asset.remote_uri,
                {},
                AssetScope.DISPATCH,
                dispatch_id,
                None,
                key,
            )
            asset.remote_uri = filtered_uri

    for key, asset in manifest.lattice.assets:
        if asset.remote_uri:
            filtered_uri = filter_asset_uri(
                URI_FILTER_POLICY, asset.remote_uri, {}, AssetScope.LATTICE, dispatch_id, None, key
            )
            asset.remote_uri = filtered_uri

    # Now filter each node
    tg = manifest.lattice.transport_graph
    for node in tg.nodes:
        for key, asset in node.assets:
            if asset.remote_uri:
                filtered_uri = filter_asset_uri(
                    URI_FILTER_POLICY,
                    asset.remote_uri,
                    {},
                    AssetScope.NODE,
                    dispatch_id,
                    node.id,
                    key,
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
    object_store: BaseProvider,
) -> ResultAssets:
    """Insert asset records and populate the asset link table"""
    asset_ids = {}

    for asset_key, asset in manifest.assets:
        storage_path, object_key = object_store.get_uri_components(
            dispatch_id=manifest.metadata.dispatch_id,
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
        asset.remote_uri = f"file://{local_uri}"

    # Write asset records to DB
    n_records = len(asset_ids)

    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} asset records took {delta} seconds")

    result_asset_links = [
        record.associate_asset(session, key, asset_rec.id) for key, asset_rec in asset_ids.items()
    ]
    n_records = len(result_asset_links)
    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} asset links took {delta} seconds")

    return manifest.assets


# To be called after import_result
def handle_redispatch(
    manifest: ResultSchema,
    parent_dispatch_id: str,
    reuse_previous_results: bool,
) -> Tuple[ResultSchema, List[Tuple[Asset, Asset]]]:
    # * Compare transport graphs (tg_ops)
    # * Copy reusable nodes (tg_ops)
    # * Handle reuse_previous_results
    # * Filter node statuses in the DB: PENDING_REPLACEMENT -> NEW_OBJECT
    # * Filter asset upload URIs for reusable nodes
    # * Return filtered manifest

    dispatch_id = manifest.metadata.dispatch_id

    # Load the full NX graph for graph diffing (only node metadata
    # will actually be loaded in memory).
    result_object = Result.from_dispatch_id(dispatch_id, bare=False)
    parent_result_object = Result.from_dispatch_id(parent_dispatch_id, bare=False)

    tg_new = result_object.lattice.transport_graph
    tg_old = parent_result_object.lattice.transport_graph

    # Get the nodes that can potentially be reused from the previous
    # dispatch, assuming that they have previously completed.
    reusable_nodes = TransportGraphOps(tg_old).get_reusable_nodes(tg_new)

    # No need to upload assets for reusable nodes since they can be
    # copied internally from the previous dispatch. Thus, don't return
    # an upload URI to the client.
    reusable_nodes_set = set(reusable_nodes)
    tg_manifest = manifest.lattice.transport_graph

    with Result.session() as session:
        for node in tg_manifest.nodes:
            if node.id in reusable_nodes_set:
                dal_node = tg_new.get_node(node.id)
                for key, asset in node.assets:
                    asset.remote_uri = ""

                    # Don't pull asset
                    dal_asset = dal_node.get_asset(key, session)
                    dal_asset.set_remote(session, "")

    # Two cases:
    #
    # If not reuse_previous_results, copy assets for all reusable
    # nodes but leave all metadata as initialized by the SDK.  This
    # will cause all nodes to be rerun since their statuses will be
    # NEW_OBJECT.

    # If reuse_previous_results, copy all assets and metadata from the
    # previous dispatch. This will cause reusable nodes with a
    # COMPLETED corresponding node in the old dispatch to be marked
    # PENDING_REUSE in the DB, signalling to the dispatcher that they
    # don't need to be re-run.
    assets_to_copy = TransportGraphOps(tg_new).copy_nodes_from(
        tg_old,
        reusable_nodes,
        copy_metadata=reuse_previous_results,
        defer_copy_objects=True,
    )

    # Since the graph comparison is finished, we can upgrade
    # PENDING_REPLACEMENT to NEW_OBJECT in the DB.
    TransportGraphOps(tg_new).reset_nodes()

    # Copy corresponding workflow assets with the same hashes and
    # don't ask the client to upload them.

    with Result.session() as session:
        for key, asset in manifest.assets:
            new_asset = result_object.get_asset(key, session)
            old_asset = parent_result_object.get_asset(key, session)
            if new_asset.digest == old_asset.digest:
                asset.remote_uri = ""
                app_log.debug(f"Copying workflow asset {key}")
                assets_to_copy.append((old_asset, new_asset))
                # Don't pull asset
                new_asset.set_remote(session, "")

        for key, asset in manifest.lattice.assets:
            new_asset = result_object.lattice.get_asset(key, session)
            old_asset = parent_result_object.lattice.get_asset(key, session)
            if new_asset.digest == old_asset.digest:
                asset.remote_uri = ""
                app_log.debug(f"Copying workflow asset {key}")
                assets_to_copy.append((old_asset, new_asset))
                # Don't pull asset
                new_asset.set_remote(session, "")

    # Copy asset metadata
    with Result.session() as session:
        for item in assets_to_copy:
            src, dest = item
            copy_asset_meta(session, src, dest)

    # Copy asset data
    # for item in assets_to_copy:
    #     src, dest = item
    #     copy_asset(src, dest)

    return manifest, assets_to_copy
