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

    def get_nodes(self, dispatch_id: str):
        """
        Get nodes from dispatch id
        When dispatch id passed to get graph
            Join lattice and electron on Electron.parent_lattice_id == Lattice.id
            then filter it with dispatch id
        Args:
            dispatch_id: Refers to the dispatch id from lattices table
        Return:
            graph data with list of nodes and links
        """
        print("node ", dispatch_id)
        sql = text(
            """SELECT electrons.id as id, electrons.name as name,
            electrons.transport_graph_node_id as node_id,
            electrons.started_at,electrons.completed_at,electrons.status,electrons.type,
            electrons.executor,
            lattices.electron_id as parent_electron_id,
            (case when electrons.type == 'sublattice'
            then 1
            else 0
            END
            ) as is_parent,
            lattices.dispatch_id as parent_dispatch_id,
            (case when electrons.type == 'sublattice'
            then
            (select lattices.dispatch_id from lattices
            join electrons on lattices.electron_id == electrons.id
            where lattices.electron_id == electrons.id)
            else Null
            END
            ) as sublattice_dispatch_id
            from electrons join lattices on electrons.parent_lattice_id == lattices.id
            where lattices.root_dispatch_id == :a
        """
        )
        result = self.db_con.execute(sql, {"a": str(dispatch_id)}).fetchall()
        return result

    def get_links(self, dispatch_id: str):
        """
        Get links from dispatch id
        When dispatch id passed to get graph
            Join lattice and electron by Electron.parent_lattice_id == Lattice.id
            Join Electron and Electron Dependency by ElectronDependency.electron_id == Electron.id
            then filter it with dispatch id
        Args:
            dispatch_id: Refers to the dispatch id from lattices table
        Return:
            graph data with list of nodes and links
        """
        return (
            self.db_con.query(
                ElectronDependency.edge_name,
                ElectronDependency.parameter_type,
                ElectronDependency.electron_id.label("target"),
                ElectronDependency.parent_electron_id.label("source"),
                ElectronDependency.arg_index,
            )
            .join(Lattice, Lattice.id == Electron.parent_lattice_id)
            .join(Electron, Electron.id == ElectronDependency.electron_id)
            .filter((Lattice.root_dispatch_id == str(dispatch_id)))
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
            Get list of nodes from Electrons table by passing list of latice id with the dispatch id
            Get list of links from Electron dependency table by passing in electron ids
        Args:
            dispatch_id: Refers to the dispatch id from lattices table
        Return:
            graph data with list of nodes and links
        """
        nodes = self.get_nodes(dispatch_id=dispatch_id)
        data = self.get_links(dispatch_id=dispatch_id)
        links = self.check_error(data=data)
        return {"dispatch_id": str(dispatch_id), "nodes": nodes, "links": links}
