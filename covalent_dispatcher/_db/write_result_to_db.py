# Copyright 2021 Agnostiq Inc.
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

"""This module contains all the functions required to save the decomposed result object in the database."""

import os
from datetime import datetime as dt
from datetime import timezone

import networkx as nx
from sqlalchemy import update
from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.defaults import (
    arg_prefix,
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
    subscript_prefix,
)
from covalent._shared_files.exceptions import MissingLatticeRecordError
from covalent._workflow.lattice import Lattice as LatticeClass

from .datastore import workflow_db
from .models import Asset, Electron, ElectronAsset, ElectronDependency, Job, Lattice, LatticeAsset

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class MissingElectronRecordError(Exception):
    """
    Exception to raise when an electron record is missing from the database
    """

    pass


class InvalidFileExtension(Exception):
    """
    Exception to raise when an invalid file extension is encountered
    """

    pass


def update_lattice_completed_electron_num(dispatch_id: str) -> None:
    """
    Update the number of completed electrons by one corresponding to a lattice
    """

    with workflow_db.session() as session:
        session.query(Lattice).filter_by(dispatch_id=dispatch_id).update(
            {
                "completed_electron_num": Lattice.completed_electron_num + 1,
                "updated_at": dt.now(timezone.utc),
            }
        )


def transaction_insert_lattices_data(
    session: Session,
    dispatch_id: str,
    electron_id: int,
    name: str,
    docstring_filename: str,
    electron_num: int,
    completed_electron_num: int,
    status: str,
    storage_type: str,
    storage_path: str,
    function_filename: str,
    function_string_filename: str,
    executor: str,
    executor_data: str,
    workflow_executor: str,
    workflow_executor_data: str,
    error_filename: str,
    inputs_filename: str,
    results_filename: str,
    hooks_filename: str,
    results_dir: str,
    root_dispatch_id: str,
    created_at: dt,
    updated_at: dt,
    started_at: dt,
    completed_at: dt,
) -> int:
    """
    This function writes the lattice data / metadata to the Lattices table in the DB

    Return(s)
        ID of the lattice updated
    """

    lattice_row = Lattice(
        dispatch_id=dispatch_id,
        electron_id=electron_id,
        name=name,
        docstring_filename=docstring_filename,
        status=status,
        electron_num=electron_num,
        completed_electron_num=completed_electron_num,
        storage_type=storage_type,
        storage_path=storage_path,
        function_filename=function_filename,
        function_string_filename=function_string_filename,
        executor=executor,
        executor_data=executor_data,
        workflow_executor=workflow_executor,
        workflow_executor_data=workflow_executor_data,
        error_filename=error_filename,
        inputs_filename=inputs_filename,
        results_filename=results_filename,
        hooks_filename=hooks_filename,
        results_dir=results_dir,
        root_dispatch_id=root_dispatch_id,
        is_active=True,
        created_at=created_at,
        updated_at=updated_at,
        started_at=started_at,
        completed_at=completed_at,
    )

    session.add(lattice_row)
    session.flush()
    lattice_id = lattice_row.id

    app_log.debug(f"returning lattice id {lattice_id}")
    return lattice_id


def insert_lattices_data(*args, **kwargs):
    """
    Execute the transaction to update lattice data in the database

    Return(s)
        None
    """
    with workflow_db.session() as session:
        transaction_insert_lattices_data(session, *args, **kwargs)
    app_log.debug(f"Added lattice record {locals()} to DB")


def transaction_insert_job_record(session: Session, cancel_requested: bool):
    job_row = Job(cancel_requested=cancel_requested)
    session.add(job_row)
    session.flush()
    return job_row


def transaction_insert_electron_asset_record(
    session: Session,
    electron_id: int,
    asset_id: int,
    key: str,
) -> ElectronAsset:
    electron_asset = ElectronAsset(
        meta_record_id=electron_id,
        asset_id=asset_id,
        key=key,
    )
    session.add(electron_asset)
    return electron_asset


def transaction_insert_lattice_asset_record(
    session: Session,
    lattice_id: int,
    asset_id: int,
    key: str,
) -> LatticeAsset:
    lattice_asset = LatticeAsset(
        meta_record_id=lattice_id,
        asset_id=asset_id,
        key=key,
    )
    session.add(lattice_asset)
    return lattice_asset


def transaction_insert_asset_record(
    session: Session,
    storage_type: str,
    storage_path: str,
    object_key: str,
    digest_alg: str,
    digest: str,
) -> Asset:
    asset_row = Asset(
        storage_type=storage_type,
        storage_path=storage_path,
        object_key=object_key,
        digest_alg=digest_alg,
        digest=digest,
    )
    session.add(asset_row)
    session.flush()
    return asset_row


def transaction_insert_electrons_data(
    session: Session,
    parent_dispatch_id: str,
    transport_graph_node_id: int,
    task_group_id: int,
    type: str,
    name: str,
    status: str,
    storage_type: str,
    storage_path: str,
    function_filename: str,
    function_string_filename: str,
    executor: str,
    executor_data: str,
    results_filename: str,
    value_filename: str,
    stdout_filename: str,
    stderr_filename: str,
    error_filename: str,
    hooks_filename: str,
    job_id: int,
    created_at: dt,
    updated_at: dt,
    started_at: dt,
    completed_at: dt,
) -> id:
    """
    This function writes the transport graph node data to the Electrons table in the DB

    Return(s)
        electron id
    """

    # Check that the foreign key corresponding to this table exists

    row = session.query(Lattice).where(Lattice.dispatch_id == parent_dispatch_id).all()
    if len(row) == 0:
        raise MissingLatticeRecordError

    parent_lattice_id = row[0].id

    electron_row = Electron(
        parent_lattice_id=parent_lattice_id,
        transport_graph_node_id=transport_graph_node_id,
        task_group_id=task_group_id,
        type=type,
        name=name,
        status=status,
        storage_type=storage_type,
        storage_path=storage_path,
        function_filename=function_filename,
        function_string_filename=function_string_filename,
        executor=executor,
        executor_data=executor_data,
        results_filename=results_filename,
        value_filename=value_filename,
        stdout_filename=stdout_filename,
        stderr_filename=stderr_filename,
        error_filename=error_filename,
        hooks_filename=hooks_filename,
        is_active=True,
        job_id=job_id,
        created_at=created_at,
        updated_at=updated_at,
        started_at=started_at,
        completed_at=completed_at,
    )

    session.add(electron_row)
    session.flush()
    electron_id = electron_row.id

    return electron_id


def insert_electrons_data(*args, **kwargs):
    """
    Execute the electron update SQLalchemy transaction

    Return(s)
        electron_id
    """
    with workflow_db.session() as session:
        app_log.debug(f"Adding electron {locals()} to DB")
        return transaction_insert_electrons_data(session, *args, **kwargs)


def transaction_insert_electron_dependency_data(
    session: Session, dispatch_id: str, lattice: LatticeClass
):
    """
    Extract electron dependencies from the lattice transport graph and add them to the DB

    Return(s)
        dependency information of an electron
    """

    # TODO - Update how we access the transport graph edges directly in favor of using some interface provied by the TransportGraph class.
    node_links = nx.readwrite.node_link_data(lattice.transport_graph._graph)["links"]

    electron_dependency_ids = []

    for edge_data in node_links:
        electron_id = (
            session.query(Lattice, Electron)
            .filter(Lattice.id == Electron.parent_lattice_id)
            .filter(Lattice.dispatch_id == dispatch_id)
            .filter(Electron.transport_graph_node_id == edge_data["target"])
            .first()
            .Electron.id
        )
        parent_electron_id = (
            session.query(Lattice, Electron)
            .filter(Lattice.id == Electron.parent_lattice_id)
            .filter(Lattice.dispatch_id == dispatch_id)
            .filter(Electron.transport_graph_node_id == edge_data["source"])
            .first()
            .Electron.id
        )

        electron_dependency_row = ElectronDependency(
            electron_id=electron_id,
            parent_electron_id=parent_electron_id,
            edge_name=edge_data["edge_name"],
            parameter_type=edge_data["param_type"] if "param_type" in edge_data else None,
            arg_index=edge_data["arg_index"] if "arg_index" in edge_data else None,
            is_active=True,
            created_at=dt.now(timezone.utc),
            updated_at=dt.now(timezone.utc),
        )

        session.add(electron_dependency_row)
        electron_dependency_ids.append(electron_dependency_row.id)

    return electron_dependency_ids


def insert_electron_dependency_data(*args, **kwargs):
    """
    persist the electron dependency information into the database

    Return(s)
        None
    """
    with workflow_db.session() as session:
        app_log.debug(f"Adding electron dependency data {locals()} to DB")
        transaction_insert_electron_dependency_data(session, *args, **kwargs)


def transaction_upsert_electron_dependency_data(
    session: Session, dispatch_id: str, lattice: LatticeClass
):
    """
    Insert electron dependency records if they don't exist
    """

    electron_dependencies_exist = (
        session.query(ElectronDependency, Electron, Lattice)
        .where(
            Electron.id == ElectronDependency.electron_id,
            Electron.parent_lattice_id == Lattice.id,
            Lattice.dispatch_id == dispatch_id,
        )
        .first()
        is not None
    )
    app_log.debug(f"electron_dependencies_exist is {electron_dependencies_exist}")
    if not electron_dependencies_exist:
        transaction_insert_electron_dependency_data(
            session=session, dispatch_id=dispatch_id, lattice=lattice
        )


def transaction_update_lattices_data(session: Session, dispatch_id: str, **kwargs) -> None:
    """This function updates the lattices record."""

    valid_update = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()

    if not valid_update:
        raise MissingLatticeRecordError

    for attr, value in kwargs.items():
        if value:
            setattr(valid_update, attr, value)

    session.add(valid_update)


def update_lattices_data(dispatch_id: str, **kwargs) -> None:
    """This function updates the lattices record."""

    with workflow_db.session() as session:
        transaction_update_lattices_data(session, dispatch_id, **kwargs)


def update_electrons_data(
    parent_dispatch_id: str,
    transport_graph_node_id: int,
    name: str,
    status: str,
    started_at: dt,
    updated_at: dt,
    completed_at: dt,
) -> None:
    """This function updates the electrons record."""

    with workflow_db.session() as session:
        parent_lattice_id = (
            session.query(Lattice).where(Lattice.dispatch_id == parent_dispatch_id).all()[0].id
        )
        valid_update = (
            session.query(Electron)
            .where(
                Electron.parent_lattice_id == parent_lattice_id,
                Electron.transport_graph_node_id == transport_graph_node_id,
            )
            .first()
            is not None
        )
        if not valid_update:
            raise MissingElectronRecordError

        session.execute(
            update(Electron)
            .where(
                Electron.parent_lattice_id == parent_lattice_id,
                Electron.transport_graph_node_id == transport_graph_node_id,
            )
            .values(
                name=name,
                status=status,
                started_at=started_at,
                updated_at=updated_at,
                completed_at=completed_at,
            )
        )


def get_electron_type(node_name: str) -> str:
    """Get the electron type (to be written to DB) given the electron node data."""

    if node_name.startswith(arg_prefix):
        return arg_prefix.strip(prefix_separator)

    elif node_name.startswith(attr_prefix):
        return attr_prefix.strip(prefix_separator)

    elif node_name.startswith(electron_dict_prefix):
        return electron_dict_prefix.strip(prefix_separator)

    elif node_name.startswith(electron_list_prefix):
        return electron_list_prefix.strip(prefix_separator)

    elif node_name.startswith(generator_prefix):
        return generator_prefix.strip(prefix_separator)

    elif node_name.startswith(parameter_prefix):
        return parameter_prefix.strip(prefix_separator)

    elif node_name.startswith(sublattice_prefix):
        return sublattice_prefix.strip(prefix_separator)

    elif node_name.startswith(subscript_prefix):
        return subscript_prefix.strip(prefix_separator)

    else:
        return "function"


def get_sublattice_electron_id(parent_dispatch_id: str, sublattice_node_id: int):
    """
    Query the electron ID is a sublattice

    Return(s)
        sublattice electron id
    """
    with workflow_db.session() as session:
        sublattice_electron_id = (
            session.query(Lattice, Electron)
            .where(
                Lattice.id == Electron.parent_lattice_id,
                Electron.transport_graph_node_id == sublattice_node_id,
                Lattice.dispatch_id == parent_dispatch_id,
            )
            .first()
            .Electron.id
        )

    return sublattice_electron_id


def resolve_electron_id(eid: int):
    """
    Given an electron's unique id, return the corresponding dispatch_id and node_id

    Return(s)
        dispatch_id of the lattice
        ID of the node within the lattice
    """
    with workflow_db.session() as session:
        row = (
            session.query(Lattice, Electron)
            .where(Electron.id == eid, Lattice.id == Electron.parent_lattice_id)
            .first()
        )
        dispatch_id = row.Lattice.dispatch_id
        node_id = row.Electron.transport_graph_node_id

    return dispatch_id, node_id


def write_lattice_error(dispatch_id: str, error: str) -> None:
    """
    Persist the lattice error into the database

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        error: Lattice error to be persisted

    Return(s)
        None
    """
    with workflow_db.session() as session:
        valid_update = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()

        if not valid_update:
            raise MissingLatticeRecordError

        with open(os.path.join(valid_update.storage_path, valid_update.error_filename), "w") as f:
            f.write(error)
