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

"""Graph Data Layer"""
from uuid import UUID

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
            electrons.qelectron_data_exists,
            electrons.executor as executor_label,
            (case when electrons.type = 'sublattice'
            then
            (select lattices.dispatch_id from lattices
            where lattices.electron_id = electrons.id)
            else Null
            END
            ) as sublattice_dispatch_id
            from electrons join lattices on electrons.parent_lattice_id = lattices.id
            where lattices.id = :a
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
            nodes = self.get_nodes(parrent_id)
            links = self.get_links(parrent_id)
            return {"dispatch_id": str(dispatch_id), "nodes": nodes, "links": links}
        return None
