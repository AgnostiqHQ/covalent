# Copyright 2021 Agnostiq Inc.
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

"""This module contains all the functions required to save the decomposed result object in the database."""

import os
from datetime import datetime as dt
from datetime import timezone

import networkx as nx
from sqlalchemy import update
from sqlalchemy.orm import Session

from covalent._data_store.datastore import DataStore
from covalent._data_store.models import Electron, ElectronDependency, Lattice

from .._shared_files.defaults import (
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


class MissingLatticeRecordError(Exception):
    pass


class MissingElectronRecordError(Exception):
    pass


def update_lattice_completed_electron_num(db: DataStore, dispatch_id: str) -> None:
    """Update the number of completed electrons by one corresponding to a lattice."""

    with Session(db.engine) as session:
        session.query(Lattice).filter_by(dispatch_id=dispatch_id).update(
            {
                "completed_electron_num": Lattice.completed_electron_num + 1,
                "updated_at": dt.now(timezone.utc),
            }
        )
        session.commit()


def insert_lattices_data(
    db: DataStore,
    dispatch_id: str,
    name: str,
    electron_num: int,
    completed_electron_num: int,
    status: str,
    storage_type: str,
    storage_path: str,
    function_filename: str,
    function_string_filename: str,
    executor_filename: str,
    error_filename: str,
    inputs_filename: str,
    results_filename: str,
    transport_graph_filename: str,
    created_at: dt,
    updated_at: dt,
    started_at: dt,
    completed_at: dt,
) -> int:
    """This funtion writes the lattice data / metadata to the Lattices table in the DB."""

    lattice_row = Lattice(
        dispatch_id=dispatch_id,
        name=name,
        status=status,
        electron_num=electron_num,
        completed_electron_num=completed_electron_num,
        storage_type=storage_type,
        storage_path=storage_path,
        function_filename=function_filename,
        function_string_filename=function_string_filename,
        executor_filename=executor_filename,
        error_filename=error_filename,
        inputs_filename=inputs_filename,
        results_filename=results_filename,
        transport_graph_filename=transport_graph_filename,
        is_active=True,
        created_at=created_at,
        updated_at=updated_at,
        started_at=started_at,
        completed_at=completed_at,
    )

    with Session(db.engine) as session:
        session.add(lattice_row)
        session.commit()
        lattice_id = lattice_row.id

    return lattice_id


def insert_electrons_data(
    db: DataStore,
    parent_dispatch_id: str,
    transport_graph_node_id: int,
    type: str,
    name: str,
    status: str,
    storage_type: str,
    storage_path: str,
    function_filename: str,
    function_string_filename: str,
    executor_filename: str,
    results_filename: str,
    value_filename: str,
    attribute_name: str,
    key_filename: str,
    stdout_filename: str,
    stderr_filename: str,
    info_filename: str,
    deps_filename: str,
    call_before_filename: str,
    call_after_filename: str,
    created_at: dt,
    updated_at: dt,
    started_at: dt,
    completed_at: dt,
) -> id:
    """This function writes the transport graph node data to the Electrons table in the DB."""

    # Check that the foreign key corresponding to this table exists
    with Session(db.engine) as session:
        row = session.query(Lattice).where(Lattice.dispatch_id == parent_dispatch_id).all()
    if len(row) == 0:
        raise MissingLatticeRecordError

    parent_lattice_id = row[0].id

    electron_row = Electron(
        parent_lattice_id=parent_lattice_id,
        transport_graph_node_id=transport_graph_node_id,
        type=type,
        name=name,
        status=status,
        storage_type=storage_type,
        storage_path=storage_path,
        function_filename=function_filename,
        function_string_filename=function_string_filename,
        executor_filename=executor_filename,
        results_filename=results_filename,
        value_filename=value_filename,
        attribute_name=attribute_name,
        key_filename=key_filename,
        stdout_filename=stdout_filename,
        stderr_filename=stderr_filename,
        info_filename=info_filename,
        deps_filename=deps_filename,
        call_before_filename=call_before_filename,
        call_after_filename=call_after_filename,
        is_active=True,
        created_at=created_at,
        updated_at=updated_at,
        started_at=started_at,
        completed_at=completed_at,
    )

    with Session(db.engine) as session:
        session.add(electron_row)
        session.commit()
        electron_id = electron_row.id

    return electron_id


def insert_electron_dependency_data(db: DataStore, dispatch_id: str, lattice: "Lattice"):
    """Extract electron dependencies from the lattice transport graph and add them to the DB."""

    # TODO - Update how we access the transport graph edges directly in favor of using some interface provied by the TransportGraph class.
    node_links = nx.readwrite.node_link_data(lattice.transport_graph._graph)["links"]

    electron_dependency_ids = []
    with Session(db.engine) as session:
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
            session.commit()
            electron_dependency_ids.append(electron_dependency_row.id)

    return electron_dependency_ids


def update_lattices_data(db: DataStore, dispatch_id: str, **kwargs) -> None:
    """This function updates the lattices record."""

    with Session(db.engine) as session:
        valid_update = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()

        if not valid_update:
            raise MissingLatticeRecordError

        for attr, value in kwargs.items():
            if value:
                setattr(valid_update, attr, value)

        session.add(valid_update)
        session.commit()


def update_electrons_data(
    db: DataStore,
    parent_dispatch_id: str,
    transport_graph_node_id: int,
    status: str,
    started_at: dt,
    updated_at: dt,
    completed_at: dt,
) -> None:
    """This function updates the electrons record."""

    with Session(db.engine) as session:
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
                status=status,
                started_at=started_at,
                updated_at=updated_at,
                completed_at=completed_at,
            )
        )
        session.commit()


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


def write_sublattice_electron_id(
    db: DataStore, parent_dispatch_id: str, sublattice_node_id: int, sublattice_dispatch_id: str
) -> None:
    """Function to attach the electron id of a sublattice in the lattice record."""

    with Session(db.engine) as session:
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
        session.execute(
            update(Lattice)
            .where(Lattice.dispatch_id == sublattice_dispatch_id)
            .values(electron_id=sublattice_electron_id, updated_at=dt.now(timezone.utc))
        )
        session.commit()


def write_lattice_error(db: DataStore, dispatch_id: str, error: str):
    with Session(db.engine) as session:
        valid_update = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()

        if not valid_update:
            raise MissingLatticeRecordError

        with open(os.path.join(valid_update.storage_path, valid_update.error_filename), "w") as f:
            f.write(error)
