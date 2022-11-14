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

"""Graph Data Layer"""
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.electron_dependency import ElectronDependency
from covalent_ui.api.v1.database.schema.lattices import Lattice


class Graph:
    """Graph data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

    def get_nodes(self, parent_lattice_id: int):
        """
        Get nodes from parent_lattice_id
        Args:
            parent_lattice_id: Refers to the parent_lattice_id in electron table
        Return:
            graph data with list of nodes
        """
        sql = text(
            """SELECT
            electrons.id as id,
            electrons.name as name,
            electrons.transport_graph_node_id as node_id,
            electrons.started_at,
            electrons.completed_at,
            electrons.status,
            electrons.type,
            electrons.executor as executor_label,
            (case when electrons.type == 'sublattice'
            then
            (select lattices.dispatch_id from lattices
            where lattices.electron_id == electrons.id)
            else Null
            END
            ) as sublattice_dispatch_id
            from electrons join lattices on electrons.parent_lattice_id == lattices.id
            where lattices.id == :a
        """
        )
        result = self.db_con.execute(sql, {"a": parent_lattice_id}).fetchall()
        return result

    def get_links(self, parent_lattice_id: int):
        """
        Get links from parent_lattice_id
        When parent_lattice_id passed to get links
            then join electrons and electron_dependency
        Args:
            parent_lattice_id: Refers to the parent_lattice_id id in electrons table
        Return:
            graph data with list of links
        """
        return (
            self.db_con.query(
                ElectronDependency.edge_name,
                ElectronDependency.parameter_type,
                ElectronDependency.electron_id.label("target"),
                ElectronDependency.parent_electron_id.label("source"),
                ElectronDependency.arg_index,
            )
            .join(Electron, Electron.id == ElectronDependency.electron_id)
            .filter(Electron.parent_lattice_id == parent_lattice_id)
            .all()
        )

    def check_error(self, data):
        """
        Helper method to rise exception if data is None

        Args:
            data: list of queried data
        Return:
            data
        Rise:
            Http Exception with status code 400 and details
        """
        if data is None:
            raise HTTPException(status_code=400, detail=["Something went wrong"])
        return data

    def get_graph(self, dispatch_id: UUID):
        """
        Get graph data from parent lattice id
        When dispatch id passed to get graph
            Get list of nodes from Electrons table by passing list of latice id
            Get list of links from Electron dependency table by passing in electron
        Args:
            dispatch_id: Refers to the dispatch id from lattices table
        Return:
            graph data with list of nodes and links
        """
        parent_lattice_id = (
            self.db_con.query(Lattice.id).where(Lattice.dispatch_id == str(dispatch_id)).first()
        )
        if parent_lattice_id is not None:
            parrent_id = parent_lattice_id[0]
            nodes = self.check_error(self.get_nodes(parrent_id))
            links = self.check_error(self.get_links(parrent_id))
            return {"dispatch_id": str(dispatch_id), "nodes": nodes, "links": links}
        return None
