# Copyright 2023 Agnostiq Inc.
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


"""Functions for updating asset metadata"""


from sqlalchemy.orm import Session

from .cache import get_cached_result_object


def update_node_asset(session: Session, dispatch_id: str, node_id: int, key: str, values: dict):
    srv_res = get_cached_result_object(dispatch_id)
    node = srv_res.lattice.transport_graph.get_node(node_id)
    asset = node.get_asset(key)
    asset.update(session, values=values)


def update_lattice_asset(session: Session, dispatch_id: str, key: str, values: dict):
    srv_res = get_cached_result_object(dispatch_id)
    asset = srv_res.lattice.get_asset(key)
    asset.update(session, values=values)


def update_dispatch_asset(session: Session, dispatch_id: str, key: str, values: dict):
    srv_res = get_cached_result_object(dispatch_id)
    asset = srv_res.get_asset(key)
    asset.update(session, values=values)
