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

"""Lattices schema"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from covalent_ui.api.v1.database.config.db import Base


class Lattice(Base):
    """Lattice

    Attributes:
        id: primary key id
        dispatch_id: id of the dispatch
        electron_id: id of node if the lattice is actually a sublattice
        name: name of the lattice function
        status: workflow status
        electron_num: Total number of electron in a workflow
        completed_electron_num: Total number of completed electron in a workflow
        storage_type: Storage backend type for data files ("local", "s3")
        storage_path: Bucket name (dispatch_id)
        function_filename: Name of the file containing the serialized function
        function_string_filename: Name of the file containing the function string
        executor_filename: Name of the file containing the serialized executor
        error_filename: Name of the file containing an error message for the electron
        results_filename: Name of the file containing the serialized output
        inputs_filename: Name of the file containing the serialized input data
        transport_graph_filename: Name of the file containing generic transport graph data
        is_active: Status of the record, 1: active and 0: inactive
        created_at: created timestamp
        updated_at: updated timestamp
        started_at: started timestamp
        completed_at: completed timestamp
    """

    __tablename__ = "lattices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dispatch_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # id of node if the lattice is actually a sublattice
    electron_id: Mapped[int] = mapped_column(Integer)

    # name of the lattice function
    name: Mapped[str] = mapped_column(Text, nullable=False)

    # name of the file containing the lattice function's docstring
    docstring_filename: Mapped[str] = mapped_column(Text)

    # Workflow status
    status: Mapped[str] = mapped_column(String(24), nullable=False)

    # Number of nodes in the lattice
    electron_num: Mapped[int] = mapped_column(Integer, nullable=False)

    # Number of completed nodes in the lattice
    completed_electron_num: Mapped[int] = mapped_column(Integer, nullable=False)

    # Storage backend type for data files ("local", "s3")
    storage_type: Mapped[str] = mapped_column(Text)

    # Bucket name (dispatch_id)
    storage_path: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized function
    function_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the function string
    function_string_filename: Mapped[str] = mapped_column(Text)

    # Short name describing the executor ("local", "dask", etc)
    executor: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized executor data
    executor_data_filename: Mapped[str] = mapped_column(Text)

    # Short name describing the workflow executor ("local", "dask", etc)
    workflow_executor: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized workflow executor data
    workflow_executor_data_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing an error message for the workflow
    error_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized input data
    inputs_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized named args
    named_args_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the serialized named kwargs
    named_kwargs_filename: Mapped[str] = mapped_column(Text)

    # name of the file containing the serialized output
    results_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the transport graph
    transport_graph_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the default electron dependencies
    deps_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the default list of callables before electrons are executed
    call_before_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the default list of callables after electrons are executed
    call_after_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the set of cova imports
    cova_imports_filename: Mapped[str] = mapped_column(Text)

    # Name of the file containing the set of lattice imports
    lattice_imports_filename: Mapped[str] = mapped_column(Text)

    # Results directory (will be deprecated soon)
    results_dir: Mapped[str] = mapped_column(Text)

    # Dispatch id of the root lattice in a hierarchy of sublattices
    root_dispatch_id: Mapped[str] = mapped_column(String(64), nullable=True)

    # Name of the mapped_column which signifies soft deletion of a lattice
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    started_at: Mapped[DateTime] = mapped_column(DateTime)
    completed_at: Mapped[DateTime] = mapped_column(DateTime)
