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

"""Unit tests for electron."""

from covalent._workflow.electron import Electron
from covalent._workflow.transport import TransportableObject, _TransportGraph


def test_electron_add_collection_node():
    """Test `to_decoded_electron_collection` in `Electron.add_collection_node`"""

    def f(x):
        return x

    e = Electron(f)
    tg = _TransportGraph()
    node_id = e.add_collection_node_to_graph(tg, prefix=":")
    collection_fn = tg.get_node_value(node_id, "function").get_deserialized()

    collection = [
        TransportableObject.make_transportable(1),
        TransportableObject.make_transportable(2),
    ]

    assert collection_fn(x=collection) == [1, 2]
