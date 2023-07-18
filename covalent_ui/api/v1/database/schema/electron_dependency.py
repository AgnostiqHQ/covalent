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

"""Electron dependency schema"""

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Unique ID of electron
    electron_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Unique ID of the electron's parent
    parent_electron_id: Mapped[int] = mapped_column(Integer, nullable=False)

    edge_name: Mapped[str] = mapped_column(Text, nullable=False)

    # arg, kwarg, null
    parameter_type: Mapped[str] = mapped_column(String(24), nullable=True)

    # Argument position - this value is null unless parameter_type is arg
    arg_index: Mapped[int] = mapped_column(Integer, nullable=True)

    # Name of the column which signifies soft deletion of the electron dependencies corresponding to a lattice
    is_active: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=True)

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True, onupdate=func.now(), server_default=func.now()
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
