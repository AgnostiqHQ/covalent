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

"""Graph functional test"""

from sqlalchemy.orm import Session

import covalent_ui.api.v1.database.config.db as db
import tests.covalent_ui_backend_tests.utils.main as main
from covalent_ui.api.v1.data_layer.graph_dal import Graph
from tests.covalent_ui_backend_tests.utils.assert_data.graph import seed_graph_data
from tests.covalent_ui_backend_tests.utils.client_template import TestClientTemplate

object_test_template = TestClientTemplate()
output_data = seed_graph_data()


def test_get_nodes():
    """Get all nodes"""
    main.init()
    dispatch_id = "78525234-72ec-42dc-94a0-f4751707f9cd"
    with Session(db.engine) as session:
        graph = Graph(session)
        graph_nodes = graph.get_nodes(dispatch_id=dispatch_id)
        main.de_init()
        assert graph_nodes == output_data["test_graph"]["case_func_get_nodes"]["response_data"]


def test_get_links():
    """Get all links"""
    main.init()
    dispatch_id = "78525234-72ec-42dc-94a0-f4751707f9cd"
    with Session(db.engine) as session:
        graph = Graph(session)
        graph_links = graph.get_links(dispatch_id=dispatch_id)
        main.de_init()
        assert graph_links == output_data["test_graph"]["case_func_get_links"]["response_data"]
