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

"""
Models for the workflows db
"""

import enum

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# See electron.py's import list and
# execution.py's _run_planned_workflow
class ElectronTypeEnum(enum.Enum):
    electron = 1
    parameter = 2
    sublattice = 3
    collection = 4
    attribute = 5
    generated = 6
    subscript = 7


class ParameterTypeEnum(enum.Enum):
    arg = 1
    kwarg = 2


class Lattice(Base):
    __tablename__ = "lattices"
    id = Column(BigInteger, primary_key=True)
    dispatch_id = Column(String(64), nullable=False)
    electron_id = Column(Integer)
    name = Column(Text, nullable=False)
    status = Column(String(24), nullable=False)
    storage_type = Column(Text)
    storage_path = Column(Text)
    function_filename = Column(Text)
    function_string_filename = Column(Text)
    executor_filename = Column(Text)
    error_filename = Column(Text)
    inputs_filename = Column(Text)
    results_filename = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class Electron(Base):
    __tablename__ = "electrons"
    id = Column(BigInteger, primary_key=True)
    parent_lattice_id = Column(BigInteger, ForeignKey("lattices.id"), nullable=False)
    transport_graph_node_id = Column(Integer, nullable=False)
    type = Column(Enum(ElectronTypeEnum), nullable=False)
    name = Column(Text, nullable=False)
    status = Column(String(24), nullable=False)
    storage_type = Column(Text)
    storage_path = Column(Text)
    function_filename = Column(Text)
    function_string_filename = Column(Text)
    executor_filename = Column(Text)
    error_filename = Column(Text)
    results_filename = Column(Text)

    # For parameter nodes
    value_filename = Column(Text)

    # For attribute nodes
    attribute_name = Column(Text)

    # For generated and subscript nodes
    key = Column(Integer)

    stdout_filename = Column(Text)
    stderr_filename = Column(Text)
    info_filename = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class ElectronDependency(Base):
    __tablename__ = "electron_dependency"
    id = Column(BigInteger, primary_key=True)
    electron_id = Column(Integer, nullable=False)
    parent_electron_id = Column(Integer, nullable=False)
    edge_name = Column(Text, nullable=False)
    parameter_type = Column(Enum(ParameterTypeEnum), nullable=False)
    created_at = Column(DateTime, nullable=False)
