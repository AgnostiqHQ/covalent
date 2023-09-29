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

"""Electron dependency schema"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from covalent_ui.api.v1.database.config.db import Base


class ElectronDependency(Base):
    """Electron Dependency

    Attributes:
        id: primary key id
        electron_id: unique electron id
        parent_electron_id: parent electron id
        edge_name: edge name for electron
        parameter_type: parameter type of enum
        arg_index: Argument Posistion
        created_at: created date
        is_active: Status of the record, 1: active and 0: inactive
    """

    __tablename__ = "electron_dependency"
    id = Column(Integer, primary_key=True)

    # Unique ID of electron
    electron_id = Column(Integer, nullable=False)

    # Unique ID of the electron's parent
    parent_electron_id = Column(Integer, nullable=False)

    edge_name = Column(Text, nullable=False)

    # arg, kwarg, null
    parameter_type = Column(String(24), nullable=True)

    # Argument position - this value is null unless parameter_type is arg
    arg_index = Column(Integer, nullable=True)

    # Name of the column which signifies soft deletion of the electron dependencies corresponding to a lattice
    is_active = Column(Boolean, nullable=False, default=True)

    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())
