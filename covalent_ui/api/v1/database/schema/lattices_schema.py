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
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from covalent_ui.api.v1.database.config.db import Base


class Lattice(Base):
    """Lattice

    Attributes:
        id: primary key id
        dispatch_id: id of the dispatch
        electron_id: id of node if the lattice is actually a sublattice
        name: name of the lattice function
        status: workflow status
        status: Execution status of the node
        storage_type: Storage backend type for data files ("local", "s3")
        storage_path: Bucket name (dispatch_id)
        function_filename: Name of the file containing the serialized function
        function_string_filename: Name of the file containing the function string
        executor_filename: Name of the file containing the serialized executor
        error_filename: Name of the file containing an error message for the electron
        results_filename: Name of the file containing the serialized output
        inputs_filename: Name of the file containing the serialized input data
        created_at: created timestamp
        updated_at: updated timestamp
        started_at: started timestamp
        completed_at: completed timestamp
    """

    __tablename__ = "lattices"
    id = Column(BigInteger, primary_key=True)
    dispatch_id = Column(String(64), nullable=False)

    electron_id = Column(Integer)

    name = Column(Text, nullable=False)

    status = Column(String(24), nullable=False)

    electron_num = Column(Integer, nullable=False)

    # Number of completed nodes in the lattice
    completed_electron_num = Column(Integer, nullable=False)

    storage_type = Column(Text)

    storage_path = Column(Text)

    function_filename = Column(Text)

    function_string_filename = Column(Text)

    executor_filename = Column(Text)

    error_filename = Column(Text)

    inputs_filename = Column(Text)

    results_filename = Column(Text)
    transport_graph_filename = Column(Text)

    is_active = Column(Boolean)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
