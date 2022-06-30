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

from datetime import datetime as dt

from sqlalchemy.orm import Session

from covalent._data_store.datastore import DataStore
from covalent._data_store.models import Lattice

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


def insert_lattices_data(
    db: DataStore,
    dispatch_id: str,
    name: str,
    status: str,
    storage_type: str,
    storage_path: str,
    function_filename: str,
    function_string_filename: str,
    executor_filename: str,
    error_filename: str,
    inputs_filename: str,
    results_filename: str,
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
        storage_type=storage_type,
        storage_path=storage_path,
        function_filename=function_filename,
        function_string_filename=function_string_filename,
        executor_filename=executor_filename,
        error_filename=error_filename,
        inputs_filename=inputs_filename,
        results_filename=results_filename,
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


def insert_electrons_data():
    pass


def insert_electron_dependency_data():
    pass


def update_lattices_data():
    pass


def update_electrons_data():
    pass


def get_electron_dependencies():
    pass


def sublattice_electron_id():
    pass


def are_electron_dependencies_added():
    pass


def is_lattice_added():
    pass


def get_electron_type(node: dict) -> str:
    """Get the electron type (to be written to DB) given the electron node data."""

    if node["name"].startswith(arg_prefix):
        return arg_prefix.strip(prefix_separator)

    elif node["name"].startswith(attr_prefix):
        return attr_prefix.strip(prefix_separator)

    elif node["name"].startswith(electron_dict_prefix):
        return electron_dict_prefix.strip(prefix_separator)

    elif node["name"].startswith(electron_list_prefix):
        return electron_list_prefix.strip(prefix_separator)

    elif node["name"].startswith(generator_prefix):
        return generator_prefix.strip(prefix_separator)

    elif node["name"].startswith(parameter_prefix):
        return parameter_prefix.strip(prefix_separator)

    elif node["name"].startswith(sublattice_prefix):
        return sublattice_prefix.strip(prefix_separator)

    elif node["name"].startswith(subscript_prefix):
        return subscript_prefix.strip(prefix_separator)

    else:
        return "function"
