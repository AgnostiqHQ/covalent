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

"""DB-backed edge"""


from typing import Dict

from .._db import models
from .controller import Record
from .db_interfaces.edge_utils import _to_edge_attrs, _to_endpoints


class Edge:
    def __init__(self, record: models.ElectronDependency, uid_node_id_map: Dict):
        self.source, self.target = _to_endpoints(record, uid_node_id_map)
        self.attrs = _to_edge_attrs(record)


class ElectronDependency(Record[models.ElectronDependency]):
    model = models.ElectronDependency
